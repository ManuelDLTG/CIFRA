"""
silver/parser.py
Parsea XMLs de CFDI 4.0 y retorna un dict con los campos normalizados.
Compatible con el schema real generado (cfdi:Comprobante v4.0 + tfd v1.1).
"""

from lxml import etree
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Namespaces del SAT
NS = {
    "cfdi": "http://www.sat.gob.mx/cfd/4",
    "tfd":  "http://www.sat.gob.mx/TimbreFiscalDigital",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _attr(element, name: str, default=None) -> Optional[str]:
    val = element.get(name)
    return val if val is not None else default


def _decimal(value: Optional[str]) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _datetime(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# Parser principal
# ---------------------------------------------------------------------------

def parse_cfdi(xml_bytes: bytes) -> dict:
    """
    Parsea un XML de CFDI 4.0 y retorna un diccionario con todos los campos.

    Args:
        xml_bytes: contenido del archivo XML en bytes.

    Returns:
        dict con los campos del CFDI normalizados y tipados.

    Raises:
        ValueError: si el XML no es un CFDI válido o falta un campo crítico.
    """
    try:
        root = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as e:
        raise ValueError(f"XML malformado: {e}")

    version = _attr(root, "Version")
    if version != "4.0":
        raise ValueError(f"Version inesperada: {version}. Se esperaba 4.0")

    # ── Comprobante ────────────────────────────────────────────────────────
    fecha_emision = _datetime(_attr(root, "Fecha"))
    total         = _decimal(_attr(root, "Total"))
    subtotal      = _decimal(_attr(root, "SubTotal"))

    if fecha_emision is None:
        raise ValueError("Campo Fecha ausente o con formato incorrecto")
    if total is None:
        raise ValueError("Campo Total ausente o no numérico")

    comprobante = {
        "version":          version,
        "serie":            _attr(root, "Serie"),
        "folio":            _attr(root, "Folio"),
        "fecha_emision":    fecha_emision,
        "subtotal":         subtotal,
        "descuento":        _decimal(_attr(root, "Descuento")),
        "total":            total,
        "moneda":           _attr(root, "Moneda", "MXN"),
        "tipo_cambio":      _decimal(_attr(root, "TipoCambio")),
        "tipo_comprobante": _attr(root, "TipoDeComprobante"),
        "metodo_pago":      _attr(root, "MetodoPago"),
        "forma_pago":       _attr(root, "FormaPago"),
        "lugar_expedicion": _attr(root, "LugarExpedicion"),
        "exportacion":      _attr(root, "ExportacionMexico"),
        "no_certificado":   _attr(root, "NoCertificado"),
    }

    # ── Emisor ─────────────────────────────────────────────────────────────
    emisor_el = root.find("cfdi:Emisor", NS)
    if emisor_el is None:
        raise ValueError("Nodo cfdi:Emisor ausente")

    emisor = {
        "rfc_emisor":     _attr(emisor_el, "Rfc"),
        "nombre_emisor":  _attr(emisor_el, "Nombre"),
        "regimen_fiscal": _attr(emisor_el, "RegimenFiscal"),
    }

    # ── Receptor ───────────────────────────────────────────────────────────
    receptor_el = root.find("cfdi:Receptor", NS)
    if receptor_el is None:
        raise ValueError("Nodo cfdi:Receptor ausente")

    receptor = {
        "rfc_receptor":              _attr(receptor_el, "Rfc"),
        "nombre_receptor":           _attr(receptor_el, "Nombre"),
        "domicilio_fiscal_receptor": _attr(receptor_el, "DomicilioFiscalReceptor"),
        "regimen_fiscal_receptor":   _attr(receptor_el, "RegimenFiscalReceptor"),
        "uso_cfdi":                  _attr(receptor_el, "UsoCFDI"),
    }

    # ── Conceptos ──────────────────────────────────────────────────────────
    conceptos = []
    for c in root.findall("cfdi:Conceptos/cfdi:Concepto", NS):
        concepto = {
            "clave_prod_serv": _attr(c, "ClaveProdServ"),
            "clave_unidad":    _attr(c, "ClaveUnidad"),
            "unidad":          _attr(c, "Unidad"),
            "descripcion":     _attr(c, "Descripcion"),
            "valor_unitario":  _decimal(_attr(c, "ValorUnitario")),
            "importe":         _decimal(_attr(c, "Importe")),
            "descuento":       _decimal(_attr(c, "Descuento")),
            "objeto_imp":      _attr(c, "ObjetoImp"),
        }
        conceptos.append(concepto)

    # ── Impuestos ──────────────────────────────────────────────────────────
    impuestos_el = root.find("cfdi:Impuestos", NS)
    iva_trasladado = None
    isr_retenido   = None

    if impuestos_el is not None:
        iva_trasladado = _decimal(_attr(impuestos_el, "TotalImpuestosTrasladados"))
        isr_retenido   = _decimal(_attr(impuestos_el, "TotalImpuestosRetenidos"))

    # ── Timbre Fiscal Digital ──────────────────────────────────────────────
    tfd_el = root.find("cfdi:Complemento/tfd:TimbreFiscalDigital", NS)
    timbre = {}

    if tfd_el is not None:
        timbre = {
            "uuid":               _attr(tfd_el, "UUID"),
            "fecha_timbrado":     _datetime(_attr(tfd_el, "FechaTimbrado")),
            "rfc_prov_certif":    _attr(tfd_el, "RfcProvCertif"),
            "no_certificado_sat": _attr(tfd_el, "NoCertificadoSAT"),
        }
    else:
        logger.warning("tfd:TimbreFiscalDigital ausente — CFDI sin timbre")

    # ── Campos de partición derivados ─────────────────────────────────────
    particion = {
        "year":  fecha_emision.year,
        "month": fecha_emision.month,
    }

    return {
        **comprobante,
        **emisor,
        **receptor,
        **timbre,
        "conceptos":      conceptos,
        "iva_trasladado": iva_trasladado,
        "isr_retenido":   isr_retenido,
        **particion,
    }


def parse_cfdi_file(path: str) -> dict:
    """Wrapper conveniente que lee un archivo del filesystem."""
    with open(path, "rb") as f:
        return parse_cfdi(f.read())
