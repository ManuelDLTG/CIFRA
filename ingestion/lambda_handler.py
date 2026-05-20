"""
ingestion/lambda_handler.py
Lambda de ingesta de CFDIs.

Flujo:
  1. Recibe XML en base64 via API Gateway (POST /upload)
  2. Valida el XML con validator.py
  3. Deposita el XML en S3 Bronze con la ruta particionada
  4. Dispara el Glue Job Bronze → Silver (opcional, configurable)
  5. Retorna UUID + ruta S3 al cliente

Variables de entorno (definidas en CloudFormation):
  S3_BUCKET      : cifra-datalake-dev
  GLUE_JOB_NAME  : cifra-bronze-to-silver
  ENVIRONMENT    : dev | staging | prod
  TRIGGER_GLUE   : "true" | "false"  (default: false)
"""

import os
import json
import base64
import logging

import boto3
from botocore.exceptions import ClientError

from ingestion.validator import validate_cfdi
from silver.parser import parse_cfdi
from bronze.s3_utils import upload_xml_to_bronze, build_bronze_key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

S3_BUCKET     = os.environ["S3_BUCKET"]
GLUE_JOB_NAME = os.environ.get("GLUE_JOB_NAME", "cifra-bronze-to-silver")
ENVIRONMENT   = os.environ.get("ENVIRONMENT", "dev")
TRIGGER_GLUE  = os.environ.get("TRIGGER_GLUE", "false").lower() == "true"

s3_client   = boto3.client("s3")
glue_client = boto3.client("glue")


# ---------------------------------------------------------------------------
# Handler principal
# ---------------------------------------------------------------------------

def handler(event, context):
    """
    Entry point de la Lambda.
    Acepta tanto invocaciones directas como via API Gateway (proxy integration).
    """
    try:
        xml_bytes, filename = _extract_xml(event)
    except (KeyError, ValueError) as e:
        logger.warning(f"Request inválido: {e}")
        return _response(400, {"error": str(e)})

    # 1. Validar
    validation = validate_cfdi(xml_bytes)
    if not validation["valid"]:
        logger.warning(f"CFDI inválido: {validation['errors']}")
        return _response(422, {
            "error": "CFDI no pasó validación",
            "details": validation["errors"],
        })

    # 2. Parsear campos necesarios para la ruta
    try:
        parsed = parse_cfdi(xml_bytes)
    except ValueError as e:
        return _response(422, {"error": f"Error parseando CFDI: {e}"})

    rfc_emisor = parsed["rfc_emisor"]
    year       = parsed["year"]
    month      = parsed["month"]
    folio      = parsed.get("folio") or parsed.get("uuid", "sin-folio")
    uuid       = parsed.get("uuid", "")

    # 3. Subir a Bronze
    try:
        s3_uri = upload_xml_to_bronze(
            xml_bytes=xml_bytes,
            bucket=S3_BUCKET,
            rfc_emisor=rfc_emisor,
            year=year,
            month=month,
            folio=folio,
            overwrite=False,
        )
    except FileExistsError:
        logger.info(f"CFDI duplicado ignorado: {uuid}")
        return _response(200, {
            "status": "duplicate",
            "message": "El CFDI ya existe en Bronze",
            "uuid": uuid,
            "s3_key": build_bronze_key(rfc_emisor, year, month, folio),
        })
    except ClientError as e:
        logger.error(f"Error S3: {e}")
        return _response(500, {"error": "Error al guardar en S3"})

    logger.info(f"CFDI guardado: {s3_uri}")

    # 4. Disparar Glue Job (opcional)
    glue_run_id = None
    if TRIGGER_GLUE:
        try:
            resp = glue_client.start_job_run(
                JobName=GLUE_JOB_NAME,
                Arguments={
                    "--RFC_FILTER":  rfc_emisor,
                    "--YEAR_FILTER": str(year),
                },
            )
            glue_run_id = resp["JobRunId"]
            logger.info(f"Glue Job disparado: {glue_run_id}")
        except ClientError as e:
            logger.warning(f"No se pudo disparar Glue Job: {e}")

    return _response(201, {
        "status": "ok",
        "uuid": uuid,
        "rfc_emisor": rfc_emisor,
        "fecha_emision": parsed["fecha_emision"].isoformat(),
        "total": str(parsed["total"]),
        "s3_uri": s3_uri,
        "glue_run_id": glue_run_id,
    })


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_xml(event: dict) -> tuple[bytes, str]:
    """
    Extrae el XML del evento. Soporta:
    - API Gateway con body en base64 (isBase64Encoded=True)
    - API Gateway con body como string XML directo
    - Invocación directa con campo 'xml_bytes' en base64
    """
    # Invocación directa
    if "xml_bytes" in event:
        return base64.b64decode(event["xml_bytes"]), event.get("filename", "cfdi.xml")

    # API Gateway proxy
    body = event.get("body", "")
    if not body:
        raise ValueError("Body vacío — se esperaba un XML de CFDI")

    is_b64 = event.get("isBase64Encoded", False)

    if is_b64:
        xml_bytes = base64.b64decode(body)
    else:
        # Intentar parsear como JSON con campo xml_base64
        try:
            parsed_body = json.loads(body)
            if "xml_base64" in parsed_body:
                xml_bytes = base64.b64decode(parsed_body["xml_base64"])
                filename  = parsed_body.get("filename", "cfdi.xml")
                return xml_bytes, filename
        except (json.JSONDecodeError, KeyError):
            pass
        # Asumir que el body ES el XML
        xml_bytes = body.encode("utf-8")

    filename = (
        event.get("queryStringParameters", {}) or {}
    ).get("filename", "cfdi.xml")

    return xml_bytes, filename


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, ensure_ascii=False, default=str),
    }
