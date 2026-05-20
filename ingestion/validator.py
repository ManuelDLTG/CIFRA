"""
ingestion/validator.py
Validaciones básicas de un XML de CFDI 4.0 antes de guardarlo en Bronze.
No reemplaza la validación del SAT — verifica estructura mínima y campos críticos.
"""

from lxml import etree
from typing import Any
import re

NS = {
    "cfdi": "http://www.sat.gob.mx/cfd/4",
    "tfd":  "http://www.sat.gob.mx/TimbreFiscalDigital",
}

RFC_PATTERN = re.compile(
    r"^([A-ZÑ&]{3,4})(\d{6})([A-Z\d]{3})$"
)

TIPOS_VALIDOS = {"I", "E", "T", "N", "P"}


def validate_cfdi(xml_bytes: bytes) -> dict[str, Any]:
    """
    Valida un XML de CFDI y retorna un dict con el resultado.

    Returns:
        {
            "valid": bool,
            "errors": list[str],   # vacío si valid=True
            "warnings": list[str], # campos opcionales ausentes
        }
    """
    errors   = []
    warnings = []

    # 1. XML bien formado
    try:
        root = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as e:
        return {"valid": False, "errors": [f"XML malformado: {e}"], "warnings": []}

    # 2. Namespace correcto (CFDI 4.0)
    if root.tag != "{http://www.sat.gob.mx/cfd/4}Comprobante":
        errors.append(
            f"Namespace incorrecto: {root.tag}. "
            "Se esperaba cfdi:Comprobante v4.0"
        )

    # 3. Versión
    version = root.get("Version")
    if version != "4.0":
        errors.append(f"Version '{version}' no soportada. Se requiere 4.0")

    # 4. Campos obligatorios del Comprobante
    required_attrs = ["Fecha", "SubTotal", "Total", "TipoDeComprobante",
                      "LugarExpedicion", "Moneda"]
    for attr in required_attrs:
        if root.get(attr) is None:
            errors.append(f"Atributo obligatorio ausente: cfdi:Comprobante/@{attr}")

    # 5. TipoDeComprobante válido
    tipo = root.get("TipoDeComprobante")
    if tipo and tipo not in TIPOS_VALIDOS:
        errors.append(
            f"TipoDeComprobante '{tipo}' inválido. "
            f"Valores válidos: {TIPOS_VALIDOS}"
        )

    # 6. Total numérico y positivo
    total_str = root.get("Total")
    if total_str:
        try:
            total = float(total_str)
            if total < 0:
                errors.append(f"Total negativo: {total}")
        except ValueError:
            errors.append(f"Total no numérico: '{total_str}'")

    # 7. Emisor
    emisor = root.find("cfdi:Emisor", NS)
    if emisor is None:
        errors.append("Nodo cfdi:Emisor ausente")
    else:
        rfc_emisor = emisor.get("Rfc", "")
        if not RFC_PATTERN.match(rfc_emisor):
            errors.append(f"RFC emisor inválido: '{rfc_emisor}'")
        if not emisor.get("RegimenFiscal"):
            errors.append("cfdi:Emisor/@RegimenFiscal ausente")

    # 8. Receptor
    receptor = root.find("cfdi:Receptor", NS)
    if receptor is None:
        errors.append("Nodo cfdi:Receptor ausente")
    else:
        rfc_receptor = receptor.get("Rfc", "")
        if not RFC_PATTERN.match(rfc_receptor) and rfc_receptor != "XAXX010101000":
            # XAXX = público en general, válido
            errors.append(f"RFC receptor inválido: '{rfc_receptor}'")
        if not receptor.get("UsoCFDI"):
            errors.append("cfdi:Receptor/@UsoCFDI ausente")

    # 9. Al menos un Concepto
    conceptos = root.findall("cfdi:Conceptos/cfdi:Concepto", NS)
    if not conceptos:
        errors.append("cfdi:Conceptos vacío — se requiere al menos un Concepto")

    # 10. Timbre Fiscal Digital (warning si ausente, no error — puede ser pre-timbrado)
    tfd = root.find("cfdi:Complemento/tfd:TimbreFiscalDigital", NS)
    if tfd is None:
        warnings.append("tfd:TimbreFiscalDigital ausente — CFDI sin timbre SAT")
    else:
        uuid = tfd.get("UUID", "")
        if len(uuid) != 36:
            errors.append(f"UUID de timbre inválido: '{uuid}'")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
