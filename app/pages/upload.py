"""
app/pages/upload.py
Página para subir CFDIs a Bronze vía API Gateway.
"""

import base64
import os

import pandas as pd
import requests
import streamlit as st

from silver.parser import parse_cfdi


API_URL = os.environ.get("API_GATEWAY_URL", "")


def format_money(value) -> str:
    """Format numeric values as MXN currency."""
    if value in (None, "—"):
        return "—"
    return f"${float(value):,.2f}"


def parse_uploaded_file(file) -> dict:
    """Parse uploaded CFDI XML and return relevant fields."""
    xml_bytes = file.getvalue()
    parsed = parse_cfdi(xml_bytes)

    return {
        "archivo": file.name,
        "uuid": parsed.get("uuid", "—"),
        "fecha": parsed.get("fecha_emision"),
        "tipo": parsed.get("tipo_comprobante"),
        "emisor": parsed.get("nombre_emisor"),
        "receptor": parsed.get("nombre_receptor"),
        "total": parsed.get("total"),
        "moneda": parsed.get("moneda"),
        "xml_bytes": xml_bytes,
    }


def send_to_bronze(record: dict) -> dict:
    """Send a parsed CFDI XML to the API Gateway ingestion endpoint."""
    xml_b64 = base64.b64encode(record["xml_bytes"]).decode()

    try:
        response = requests.post(
            API_URL,
            json={
                "xml_base64": xml_b64,
                "filename": record["archivo"],
            },
            timeout=30,
        )

        try:
            data = response.json()
        except ValueError:
            data = {
                "status": "error",
                "message": response.text,
            }

        return {
            "archivo": record["archivo"],
            "http_status": response.status_code,
            "status": data.get("status", "error"),
            "message": data.get("message", data.get("error", "sin detalle")),
            "uuid": data.get("uuid", record["uuid"]),
            "total": data.get("total", format_money(record["total"])),
        }

    except Exception as error:
        return {
            "archivo": record["archivo"],
            "http_status": "—",
            "status": "error",
            "message": str(error),
            "uuid": record["uuid"],
            "total": format_money(record["total"]),
        }


def show():
    st.title("Subir CFDIs")
    st.caption(
        "Carga XMLs CFDI 4.0 para iniciar el flujo de ingesta: "
        "Bronze → Silver → Gold → ML."
    )

    st.info(
        "Los archivos cargados se validan localmente, se extraen sus campos "
        "principales y posteriormente pueden enviarse a la capa Bronze en S3."
    )

    uploaded = st.file_uploader(
        "Selecciona uno o varios archivos XML",
        type=["xml"],
        accept_multiple_files=True,
    )

    if not uploaded:
        st.markdown("#### Estado de ingesta")
        col1, col2, col3 = st.columns(3)
        col1.metric("Archivos seleccionados", "0")
        col2.metric("Validación CFDI", "Pendiente")
        col3.metric("Destino", "S3 Bronze")
        st.info("Arrastra tus XMLs CFDI aquí o usa el botón de carga.")
        return

    parsed_records = []
    errors = []

    for file in uploaded:
        try:
            parsed_records.append(parse_uploaded_file(file))
        except Exception as error:
            errors.append(
                {
                    "archivo": file.name,
                    "error": str(error),
                }
            )

    st.markdown("### Validación de archivos")

    col1, col2, col3 = st.columns(3)
    col1.metric("Archivos seleccionados", len(uploaded))
    col2.metric("CFDIs válidos", len(parsed_records))
    col3.metric("Errores", len(errors))

    if errors:
        st.error("Algunos archivos no pudieron validarse como CFDI 4.0.")
        st.dataframe(pd.DataFrame(errors), use_container_width=True)

    if not parsed_records:
        st.warning("No hay CFDIs válidos para enviar al pipeline.")
        return

    preview_df = pd.DataFrame(
        [
            {
                "archivo": record["archivo"],
                "uuid": record["uuid"],
                "fecha": record["fecha"],
                "tipo": record["tipo"],
                "emisor": record["emisor"],
                "receptor": record["receptor"],
                "total": format_money(record["total"]),
                "moneda": record["moneda"],
            }
            for record in parsed_records
        ]
    )

    st.markdown("### Vista previa de CFDIs válidos")
    st.dataframe(preview_df, use_container_width=True)

    total_carga = sum(
        float(record["total"])
        for record in parsed_records
        if record["total"] is not None
    )

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Monto total de la carga", format_money(total_carga))
    col_b.metric("Moneda", preview_df["moneda"].mode().iloc[0])
    col_c.metric("Tipo principal", preview_df["tipo"].mode().iloc[0])

    st.markdown("---")

    if not API_URL:
        st.warning(
            "No se encontró `API_GATEWAY_URL`. La app puede validar y previsualizar "
            "XMLs, pero aún no enviarlos al pipeline en AWS."
        )
        return

    if st.button("Enviar CFDIs válidos a Bronze", type="primary"):
        resultados = []
        progress = st.progress(0)

        for idx, record in enumerate(parsed_records):
            resultados.append(send_to_bronze(record))
            progress.progress((idx + 1) / len(parsed_records))

        results_df = pd.DataFrame(resultados)

        valid_statuses = ["success", "duplicate", "ok"]

        if results_df["status"].isin(valid_statuses).all():
            st.success(
                f"{len(parsed_records)} archivo(s) procesados correctamente."
            )
        else:
            st.warning(
                "La solicitud terminó, pero al menos un archivo tuvo error. "
                "Revisa la columna `message`."
            )

        st.dataframe(results_df, use_container_width=True)


if __name__ == "__main__":
    show()