"""
app/utils/athena_connector.py
Utilidades para leer datos de Gold y Silver desde Streamlit.
"""

import os
import awswrangler as wr
import pandas as pd
import boto3

S3_BUCKET  = os.environ.get("S3_BUCKET", "cifra-datalake-dev")
ATHENA_DB  = os.environ.get("GLUE_DATABASE", "cifra_db")
ATHENA_OUT = f"s3://{S3_BUCKET}/athena-results/"
GOLD_PATH  = f"s3://{S3_BUCKET}/gold/"


def read_gold(table: str) -> pd.DataFrame:
    """Lee una tabla Gold directamente desde S3 (rápido, sin Athena)."""
    path = f"{GOLD_PATH}{table}/"
    return wr.s3.read_parquet(path=path, dataset=True)


def query_silver(sql: str) -> pd.DataFrame:
    """Corre una query ad-hoc contra Silver en Athena."""
    return wr.athena.read_sql_query(
        sql=sql,
        database=ATHENA_DB,
        s3_output=ATHENA_OUT,
    )


def get_serie_temporal() -> pd.DataFrame:
    df = read_gold("serie_temporal")
    df["total_facturado"] = df["total_facturado"].round(2)
    df["periodo"] = df["periodo"].astype(str)
    df = df.sort_values(["year", "month"])
    return df


def get_top_clientes() -> pd.DataFrame:
    df = read_gold("top_clientes")
    df["total_facturado"] = df["total_facturado"].round(2)
    return df.sort_values("total_facturado", ascending=False)


def get_distribucion_tipos() -> pd.DataFrame:
    df = read_gold("distribucion_tipos")
    df["total_facturado"] = df["total_facturado"].round(2)
    tipo_map = {"I": "Ingreso", "E": "Egreso", "T": "Traslado", "N": "Nómina"}
    df["tipo_nombre"] = df["tipo_comprobante"].map(tipo_map)
    return df


def get_distribucion_pago() -> pd.DataFrame:
    df = read_gold("distribucion_pago")
    df["total_facturado"] = df["total_facturado"].round(2)
    return df


def get_distribucion_uso() -> pd.DataFrame:
    df = read_gold("distribucion_uso")
    df["total_facturado"] = df["total_facturado"].round(2)
    return df