"""
gold/aggregations.py
Ejecuta las queries Gold contra Athena y guarda resultados en S3.
Usa awswrangler para simplificar la integración Athena → S3.
"""

import os
import logging
import awswrangler as wr
import pandas as pd
from gold.athena_queries import (
    SERIE_TEMPORAL,
    TOP_CLIENTES,
    DISTRIBUCION_TIPOS,
    DISTRIBUCION_PAGO,
    DISTRIBUCION_USO_CFDI,
)

logger = logging.getLogger(__name__)

S3_BUCKET   = os.environ.get("S3_BUCKET", "cifra-datalake-dev")
ATHENA_DB   = os.environ.get("GLUE_DATABASE", "cifra_db")
ATHENA_OUT  = f"s3://{S3_BUCKET}/athena-results/"
GOLD_PATH   = f"s3://{S3_BUCKET}/gold/"


def run_query(sql: str, name: str) -> pd.DataFrame:
    """Ejecuta una query en Athena y retorna un DataFrame."""
    logger.info(f"Corriendo query: {name}")
    df = wr.athena.read_sql_query(
        sql=sql,
        database=ATHENA_DB,
        s3_output=ATHENA_OUT,
    )
    logger.info(f"  {name}: {len(df):,} filas")
    return df


def save_gold(df: pd.DataFrame, name: str):
    """Guarda un DataFrame como Parquet en la capa Gold."""
    path = f"{GOLD_PATH}{name}/"
    wr.s3.to_parquet(
        df=df,
        path=path,
        dataset=True,
        mode="overwrite",
    )
    logger.info(f"  Guardado en {path}")


def build_gold():
    """Construye todas las tablas Gold."""
    queries = {
        "serie_temporal":      SERIE_TEMPORAL,
        "top_clientes":        TOP_CLIENTES,
        "distribucion_tipos":  DISTRIBUCION_TIPOS,
        "distribucion_pago":   DISTRIBUCION_PAGO,
        "distribucion_uso":    DISTRIBUCION_USO_CFDI,
    }

    results = {}
    for name, sql in queries.items():
        df = run_query(sql, name)
        save_gold(df, name)
        results[name] = df

    logger.info("Gold completo.")
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    build_gold()