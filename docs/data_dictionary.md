# Diccionario de datos — CIFRA Silver

| Campo | Tipo | Fuente XML | Descripción |
|-------|------|-----------|-------------|
| uuid | string | cfdi:Complemento/tfd:TimbreFiscalDigital/@UUID | Folio fiscal único |
| fecha_emision | timestamp | cfdi:Comprobante/@Fecha | Fecha y hora de emisión |
| rfc_emisor | string | cfdi:Emisor/@Rfc | RFC del emisor |
| nombre_emisor | string | cfdi:Emisor/@Nombre | Razón social emisor |
| rfc_receptor | string | cfdi:Receptor/@Rfc | RFC del receptor |
| nombre_receptor | string | cfdi:Receptor/@Nombre | Razón social receptor |
| uso_cfdi | string | cfdi:Receptor/@UsoCFDI | Clave c_UsoCFDI |
| subtotal | decimal | cfdi:Comprobante/@SubTotal | Subtotal antes de impuestos |
| descuento | decimal | cfdi:Comprobante/@Descuento | Descuento aplicado |
| total | decimal | cfdi:Comprobante/@Total | Total de la factura |
| moneda | string | cfdi:Comprobante/@Moneda | Clave de moneda (MXN, USD…) |
| tipo_cambio | decimal | cfdi:Comprobante/@TipoCambio | Tipo de cambio si aplica |
| tipo_comprobante | string | cfdi:Comprobante/@TipoDeComprobante | I=Ingreso, E=Egreso, T=Traslado |
| metodo_pago | string | cfdi:Comprobante/@MetodoPago | PUE / PPD |
| forma_pago | string | cfdi:Comprobante/@FormaPago | Clave c_FormaPago |
| regimen_fiscal | string | cfdi:Emisor/@RegimenFiscal | Clave c_RegimenFiscal |
| conceptos | array | cfdi:Conceptos/cfdi:Concepto | Lista de conceptos (cantidad, descripción, valor) |
| iva_trasladado | decimal | cfdi:Impuestos/@TotalImpuestosTrasladados | IVA total trasladado |
| year | int | Partición derivada de fecha_emision | Año (partition key) |
| month | int | Partición derivada de fecha_emision | Mes (partition key) |
