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
    if value in (None, "—"):
        return "—"
    return f"${float(value):,.2f}"


def parse_uploaded_file(file) -> dict:
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
            errors.append({"archivo": file.name, "error": str(error)})

    st.markdown("### Validación de archivos")

    col1, col2, col3 = st.columns(3)
    col1.metric("Archivos seleccionados", len(uploaded))
    col2.metric("CFDIs válidos", len(parsed_records))
    col3.metric("Errores", len(errors))

    if errors:
        st.error("Algunos archivos no pudieron validarse como CFDI 4.0.")
        st.dataframe(pd.DataFrame(errors), use_container_width=True)

    if parsed_records:
        preview_df = pd.DataFrame(
            [
                {
                    "archivo": r["archivo"],
                    "uuid": r["uuid"],
                    "fecha": r["fecha"],
                    "tipo": r["tipo"],
                    "emisor": r["emisor"],
                    "receptor": r["receptor"],
                    "total": format_money(r["total"]),
                    "moneda": r["moneda"],
                }
                for r in parsed_records
            ]
        )

        st.markdown("### Vista previa de CFDIs válidos")
        st.dataframe(preview_df, use_container_width=True)

        total_carga = sum(float(r["total"]) for r in parsed_records if r["total"] is not None)

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
                data = response.json()

                resultados.append(
                    {
                        "archivo": record["archivo"],
                        "status": data.get("status", "error"),
                        "uuid": data.get("uuid", record["uuid"]),
                        "total": data.get("total", format_money(record["total"])),
                    }
                )
            except Exception as error:
                resultados.append(
                    {
                        "archivo": record["archivo"],
                        "status": "error",
                        "uuid": record["uuid"],
                        "total": str(error),
                    }
                )

            progress.progress((idx + 1) / len(parsed_records))

        st.success(f"{len(parsed_records)} archivo(s) enviados al pipeline.")
        st.dataframe(pd.DataFrame(resultados), use_container_width=True)


if __name__ == "__main__":
    show()