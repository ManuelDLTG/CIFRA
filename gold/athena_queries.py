"""
gold/athena_queries.py
Queries Athena para construir la capa Gold de CIFRA.
Resultados se guardan en s3://cifra-datalake-dev/gold/
"""

# ── Ingresos mensuales ─────────────────────────────────────────────────────

INGRESOS_MENSUALES = """
INSERT INTO cifra_db.cfdi_gold_ingresos
SELECT
    rfc_emisor,
    year,
    month,
    COUNT(*)                            AS num_cfdis,
    SUM(CAST(total AS double))          AS total_facturado,
    SUM(CAST(subtotal AS double))       AS subtotal_facturado,
    SUM(CAST(iva_trasladado AS double)) AS iva_total,
    AVG(CAST(total AS double))          AS ticket_promedio,
    MAX(CAST(total AS double))          AS ticket_maximo,
    MIN(CAST(total AS double))          AS ticket_minimo
FROM cifra_db.cfdi_silver
WHERE tipo_comprobante = 'I'
GROUP BY rfc_emisor, year, month
"""

# ── Top clientes ───────────────────────────────────────────────────────────

TOP_CLIENTES = """
SELECT
    rfc_receptor,
    nombre_receptor,
    COUNT(*)                        AS num_cfdis,
    SUM(CAST(total AS double))      AS total_facturado,
    MIN(fecha_emision)              AS primera_factura,
    MAX(fecha_emision)              AS ultima_factura
FROM cifra_db.cfdi_silver
WHERE tipo_comprobante = 'I'
GROUP BY rfc_receptor, nombre_receptor
ORDER BY total_facturado DESC
LIMIT 20
"""

# ── Serie temporal para forecasting ───────────────────────────────────────

SERIE_TEMPORAL = """
SELECT
    rfc_emisor,
    year,
    month,
    CAST(year AS varchar) || '-' ||
        LPAD(CAST(month AS varchar), 2, '0') AS periodo,
    COUNT(*)                            AS num_cfdis,
    SUM(CAST(total AS double))          AS total_facturado,
    SUM(CAST(iva_trasladado AS double)) AS iva_total
FROM cifra_db.cfdi_silver
WHERE tipo_comprobante = 'I'
GROUP BY rfc_emisor, year, month
ORDER BY rfc_emisor, year, month
"""

# ── Distribución por tipo de comprobante ──────────────────────────────────

DISTRIBUCION_TIPOS = """
SELECT
    tipo_comprobante,
    COUNT(*)                        AS num_cfdis,
    SUM(CAST(total AS double))      AS total_facturado,
    AVG(CAST(total AS double))      AS ticket_promedio
FROM cifra_db.cfdi_silver
GROUP BY tipo_comprobante
ORDER BY total_facturado DESC
"""

# ── Distribución por forma de pago ────────────────────────────────────────

DISTRIBUCION_PAGO = """
SELECT
    metodo_pago,
    forma_pago,
    COUNT(*)                        AS num_cfdis,
    SUM(CAST(total AS double))      AS total_facturado
FROM cifra_db.cfdi_silver
WHERE tipo_comprobante = 'I'
GROUP BY metodo_pago, forma_pago
ORDER BY total_facturado DESC
"""

# ── Distribución por uso CFDI ─────────────────────────────────────────────

DISTRIBUCION_USO_CFDI = """
SELECT
    uso_cfdi,
    COUNT(*)                        AS num_cfdis,
    SUM(CAST(total AS double))      AS total_facturado
FROM cifra_db.cfdi_silver
WHERE tipo_comprobante = 'I'
GROUP BY uso_cfdi
ORDER BY total_facturado DESC
"""