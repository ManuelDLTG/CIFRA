"""
bronze/s3_utils.py
Utilidades para depositar XMLs de CFDI en la capa Bronze de S3.
Estructura: s3://{bucket}/bronze/cfdis/rfc={RFC}/year={YYYY}/month={MM}/
"""

import boto3
import logging
from pathlib import Path
from typing import Union
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cliente S3
# ---------------------------------------------------------------------------

def get_s3_client(region: str = "us-east-1"):
    return boto3.client("s3", region_name=region)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def build_bronze_key(rfc_emisor: str, year: int, month: int, folio: str) -> str:
    """
    Retorna la ruta S3 para un CFDI en Bronze.
    Ejemplo: bronze/cfdis/rfc=EMP010101ABC/year=2024/month=01/F00143177.xml
    """
    return (
        f"bronze/cfdis/"
        f"rfc={rfc_emisor}/"
        f"year={year}/"
        f"month={month:02d}/"
        f"{folio}.xml"
    )


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

def upload_xml_to_bronze(
    xml_bytes: bytes,
    bucket: str,
    rfc_emisor: str,
    year: int,
    month: int,
    folio: str,
    region: str = "us-east-1",
    overwrite: bool = False,
) -> str:
    """
    Sube un XML de CFDI a la capa Bronze en S3.

    Args:
        xml_bytes  : contenido del XML en bytes.
        bucket     : nombre del bucket S3 (ej. 'cifra-datalake-dev').
        rfc_emisor : RFC del emisor, usado como partición.
        year       : año de emisión.
        month      : mes de emisión.
        folio      : folio del CFDI, usado como nombre de archivo.
        region     : región AWS.
        overwrite  : si False, no sobreescribe si el archivo ya existe.

    Returns:
        s3_uri: URI completa del objeto subido (s3://bucket/key).

    Raises:
        FileExistsError: si el archivo ya existe y overwrite=False.
        ClientError: si ocurre un error de AWS.
    """
    s3 = get_s3_client(region)
    key = build_bronze_key(rfc_emisor, year, month, folio)

    if not overwrite:
        try:
            s3.head_object(Bucket=bucket, Key=key)
            raise FileExistsError(
                f"El CFDI ya existe en Bronze: s3://{bucket}/{key}. "
                "Usa overwrite=True para reemplazarlo."
            )
        except ClientError as e:
            if e.response["Error"]["Code"] != "404":
                raise

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=xml_bytes,
        ContentType="application/xml",
        Metadata={
            "rfc-emisor": rfc_emisor,
            "year": str(year),
            "month": str(month),
            "folio": folio,
        },
    )

    s3_uri = f"s3://{bucket}/{key}"
    logger.info(f"CFDI subido a Bronze: {s3_uri}")
    return s3_uri


def upload_xml_file_to_bronze(
    file_path: Union[str, Path],
    bucket: str,
    rfc_emisor: str,
    year: int,
    month: int,
    folio: str,
    region: str = "us-east-1",
    overwrite: bool = False,
) -> str:
    """Wrapper que lee un archivo local y lo sube a Bronze."""
    with open(file_path, "rb") as f:
        return upload_xml_to_bronze(
            xml_bytes=f.read(),
            bucket=bucket,
            rfc_emisor=rfc_emisor,
            year=year,
            month=month,
            folio=folio,
            region=region,
            overwrite=overwrite,
        )


# ---------------------------------------------------------------------------
# Listar / descargar
# ---------------------------------------------------------------------------

def list_bronze_xmls(
    bucket: str,
    rfc_emisor: str = None,
    year: int = None,
    month: int = None,
    region: str = "us-east-1",
) -> list[str]:
    """
    Lista las claves de XMLs en Bronze, con filtros opcionales por RFC/año/mes.

    Returns:
        Lista de claves S3 (strings).
    """
    s3 = get_s3_client(region)

    prefix = "bronze/cfdis/"
    if rfc_emisor:
        prefix += f"rfc={rfc_emisor}/"
    if year:
        prefix += f"year={year}/"
    if month:
        prefix += f"month={month:02d}/"

    paginator = s3.get_paginator("list_objects_v2")
    keys = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            if obj["Key"].endswith(".xml"):
                keys.append(obj["Key"])

    logger.info(f"Encontrados {len(keys)} XMLs en Bronze con prefix '{prefix}'")
    return keys


def download_xml_from_bronze(
    bucket: str,
    key: str,
    region: str = "us-east-1",
) -> bytes:
    """Descarga un XML de Bronze y retorna sus bytes."""
    s3 = get_s3_client(region)
    response = s3.get_object(Bucket=bucket, Key=key)
    return response["Body"].read()
