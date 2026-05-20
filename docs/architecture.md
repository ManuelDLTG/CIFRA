# Arquitectura CIFRA

Documentación detallada de la arquitectura AWS y decisiones de diseño.

## Diagrama de flujo
_Ver README.md_

## Decisiones de diseño

### ¿Por qué Parquet en Silver/Gold?
- Columnar: queries Athena leen solo las columnas necesarias → costo menor
- Compresión Snappy reduce ~5x el tamaño vs XML
- Compatible nativo con Glue, Athena y SageMaker

### Particionamiento Bronze
`s3://cifra-datalake/bronze/cfdis/rfc=XAXX010101000/year=2024/month=01/`

### Schema CFDI 4.0
Campos principales extraídos en Silver — ver `silver/schemas/cfdi_40.json`
