"""
silver/glue_job.py
AWS Glue Job: Bronze (XML) → Silver (Parquet).

Lee XMLs desde S3 Bronze, los parsea con silver.parser,
y escribe Parquet particionado en S3 Silver.
Registra la tabla en Glue Data Catalog (cifra_db.cfdi_silver).

Ejecutar en Glue Studio con:
  --JOB_NAME        cifra-bronze-to-silver
  --S3_BUCKET       cifra-datalake-dev
  --GLUE_DATABASE   cifra_db
  --GLUE_TABLE      cfdi_silver
  --RFC_FILTER      (opcional) RFC específico a procesar
  --YEAR_FILTER     (opcional) año específico a procesar
"""

import sys
import json
import logging
from decimal import Decimal
from datetime import datetime

import boto3
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField,
    StringType, DoubleType, TimestampType,
    IntegerType, ArrayType
)

# Importar parser local
# En Glue, los módulos de --extra-py-files quedan en la raíz del PYTHONPATH
# sin estructura de paquete — se importan directamente por nombre de archivo
try:
    from parser import parse_cfdi          # cuando viene de glue_libs.zip
except ImportError:
    from silver.parser import parse_cfdi   # ejecución local

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Schema Spark para Silver
# ---------------------------------------------------------------------------

CONCEPTO_SCHEMA = StructType([
    StructField("clave_prod_serv", StringType()),
    StructField("clave_unidad",    StringType()),
    StructField("unidad",          StringType()),
    StructField("descripcion",     StringType()),
    StructField("valor_unitario",  DoubleType()),
    StructField("importe",         DoubleType()),
    StructField("descuento",       DoubleType()),
    StructField("objeto_imp",      StringType()),
])

SILVER_SCHEMA = StructType([
    StructField("version",          StringType()),
    StructField("serie",            StringType()),
    StructField("folio",            StringType()),
    StructField("fecha_emision",    TimestampType()),
    StructField("subtotal",         DoubleType()),
    StructField("descuento",        DoubleType()),
    StructField("total",            DoubleType()),
    StructField("moneda",           StringType()),
    StructField("tipo_cambio",      DoubleType()),
    StructField("tipo_comprobante", StringType()),
    StructField("metodo_pago",      StringType()),
    StructField("forma_pago",       StringType()),
    StructField("lugar_expedicion", StringType()),
    StructField("exportacion",      StringType()),
    StructField("no_certificado",   StringType()),
    StructField("rfc_emisor",       StringType()),
    StructField("nombre_emisor",    StringType()),
    StructField("regimen_fiscal",   StringType()),
    StructField("rfc_receptor",               StringType()),
    StructField("nombre_receptor",            StringType()),
    StructField("domicilio_fiscal_receptor",  StringType()),
    StructField("regimen_fiscal_receptor",    StringType()),
    StructField("uso_cfdi",                   StringType()),
    StructField("uuid",               StringType()),
    StructField("fecha_timbrado",     TimestampType()),
    StructField("rfc_prov_certif",    StringType()),
    StructField("no_certificado_sat", StringType()),
    StructField("iva_trasladado", DoubleType()),
    StructField("isr_retenido",   DoubleType()),
    StructField("conceptos", ArrayType(CONCEPTO_SCHEMA)),
    StructField("year",  IntegerType()),
    StructField("month", IntegerType()),
])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_row(parsed: dict) -> dict:
    """Convierte Decimal a float para DoubleType de Spark."""
    row = dict(parsed)
    decimal_fields = [
        "subtotal", "descuento", "total", "tipo_cambio",
        "iva_trasladado", "isr_retenido",
    ]
    for field in decimal_fields:
        val = row.get(field)
        row[field] = float(val) if val is not None else None

    conceptos = []
    for c in row.get("conceptos", []):
        c2 = dict(c)
        for f in ["valor_unitario", "importe", "descuento"]:
            v = c2.get(f)
            c2[f] = float(v) if v is not None else None
        conceptos.append(c2)
    row["conceptos"] = conceptos
    return row


def list_bronze_keys(s3_client, bucket: str, rfc_filter=None, year_filter=None) -> list:
    prefix = "bronze/cfdis/"
    if rfc_filter:
        prefix += f"rfc={rfc_filter}/"
    if year_filter:
        prefix += f"year={year_filter}/"

    paginator = s3_client.get_paginator("list_objects_v2")
    keys = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            if obj["Key"].endswith(".xml"):
                keys.append(obj["Key"])
    return keys


# ---------------------------------------------------------------------------
# Job principal
# ---------------------------------------------------------------------------

def run():
    args = getResolvedOptions(sys.argv, [
        "JOB_NAME",
        "S3_BUCKET",
        "GLUE_DATABASE",
        "GLUE_TABLE",
    ])

    # Opcionales
    rfc_filter  = next((a.split("=")[1] for a in sys.argv if a.startswith("--RFC_FILTER=")), None)
    year_filter = next((a.split("=")[1] for a in sys.argv if a.startswith("--YEAR_FILTER=")), None)

    bucket   = args["S3_BUCKET"]
    database = args["GLUE_DATABASE"]
    table    = args["GLUE_TABLE"]

    sc          = SparkContext()
    glue_ctx    = GlueContext(sc)
    spark       = glue_ctx.spark_session
    job         = Job(glue_ctx)
    job.init(args["JOB_NAME"], args)

    s3 = boto3.client("s3")

    logger.info(f"Listando XMLs en Bronze — bucket={bucket} rfc={rfc_filter} year={year_filter}")
    keys = list_bronze_keys(s3, bucket, rfc_filter, year_filter)
    logger.info(f"Total XMLs a procesar: {len(keys)}")

    if not keys:
        logger.warning("No se encontraron XMLs en Bronze. Terminando.")
        job.commit()
        return

    # Procesar en lotes usando RDD para paralelismo
    keys_rdd = sc.parallelize(keys, numSlices=min(len(keys), 200))

    def process_key(key):
        import boto3
        try:
            from parser import parse_cfdi
        except ImportError:
            from silver.parser import parse_cfdi
        s3_local = boto3.client("s3")
        try:
            resp = s3_local.get_object(Bucket=bucket, Key=key)
            xml_bytes = resp["Body"].read()
            parsed = parse_cfdi(xml_bytes)
            return [_to_row(parsed)]
        except Exception as e:
            logger.error(f"Error procesando {key}: {e}")
            return []

    rows_rdd = keys_rdd.flatMap(process_key)
    df = spark.createDataFrame(rows_rdd, schema=SILVER_SCHEMA)

    # Ruta Silver particionada
    silver_path = f"s3://{bucket}/silver/cfdis/"

    logger.info(f"Escribiendo Parquet en {silver_path}")
    (
        df.write
        .mode("append")
        .partitionBy("rfc_emisor", "year", "month")
        .parquet(silver_path)
    )

    # Registrar/actualizar tabla en Glue Catalog
    logger.info(f"Actualizando Glue Catalog: {database}.{table}")
    glue_client = boto3.client("glue")
    try:
        glue_client.delete_table(DatabaseName=database, Name=table)
    except glue_client.exceptions.EntityNotFoundException:
        pass

    glue_client.create_table(
        DatabaseName=database,
        TableInput={
            "Name": table,
            "StorageDescriptor": {
                "Columns": [
                    {"Name": f.name, "Type": _spark_type_to_glue(f.dataType)}
                    for f in SILVER_SCHEMA.fields
                    if f.name not in ("year", "month", "rfc_emisor")
                ],
                "Location": silver_path,
                "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
                "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
                "SerdeInfo": {
                    "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe",
                },
            },
            "PartitionKeys": [
                {"Name": "rfc_emisor", "Type": "string"},
                {"Name": "year",       "Type": "int"},
                {"Name": "month",      "Type": "int"},
            ],
            "TableType": "EXTERNAL_TABLE",
            "Parameters": {"classification": "parquet"},
        },
    )

    count = df.count()
    logger.info(f"Job completado. Registros escritos: {count:,}")
    job.commit()


def _spark_type_to_glue(spark_type) -> str:
    """Mapeo básico de tipos Spark a Glue/Hive."""
    from pyspark.sql.types import (
        StringType, DecimalType, TimestampType,
        IntegerType, ArrayType, StructType
    )
    if isinstance(spark_type, StringType):    return "string"
    if isinstance(spark_type, IntegerType):   return "int"
    if isinstance(spark_type, TimestampType): return "timestamp"
    if isinstance(spark_type, DecimalType):   return f"decimal({spark_type.precision},{spark_type.scale})"
    if isinstance(spark_type, ArrayType):     return "string"  # serializado como JSON en Athena
    return "string"


if __name__ == "__main__":
    run()
