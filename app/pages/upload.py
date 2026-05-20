"""
app/pages/upload.py
Página para subir CFDIs a Bronze via API Gateway.
"""

import streamlit as st
import requests
import base64
import os

API_URL = os.environ.get("API_GATEWAY_URL", "")


def show():
    st.title("Subir CFDIs")
    st.caption("Sube archivos XML de CFDI 4.0 para procesarlos en el pipeline")

    uploaded = st.file_uploader(
        "Selecciona uno o varios archivos XML",
        type=["xml"],
        accept_multiple_files=True,
    )

    if not uploaded:
        st.info("Arrastra tus archivos XML aquí o usa el botón de arriba.")
        return

    st.write(f"**{len(uploaded)} archivo(s) seleccionado(s)**")

    if st.button("Subir al pipeline", type="primary"):
        resultados = []
        progress = st.progress(0)

        for i, file in enumerate(uploaded):
            xml_bytes = file.read()
            xml_b64   = base64.b64encode(xml_bytes).decode()

            try:
                resp = requests.post(
                    API_URL,
                    json={"xml_base64": xml_b64, "filename": file.name},
                    timeout=30,
                )
                data = resp.json()
                resultados.append({
                    "archivo": file.name,
                    "status":  data.get("status", "error"),
                    "uuid":    data.get("uuid", "—"),
                    "total":   data.get("total", "—"),
                })
            except Exception as e:
                resultados.append({
                    "archivo": file.name,
                    "status":  "error",
                    "uuid":    "—",
                    "total":   str(e),
                })

            progress.progress((i + 1) / len(uploaded))

        st.success(f"{len(uploaded)} archivo(s) procesado(s)")
        st.dataframe(resultados, use_container_width=True)