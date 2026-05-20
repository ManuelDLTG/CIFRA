"""
app/pages/forecast.py
Página de forecast de cash flow.
Placeholder — se conecta al modelo de SageMaker en Fase 4.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from app.utils.athena_connector import get_serie_temporal


def show():
    st.title("Forecast de cash flow")
    st.caption("Predicción de ingresos para los próximos 3 meses")

    with st.spinner("Cargando serie temporal..."):
        serie = get_serie_temporal()

    # Serie histórica
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=serie["periodo"],
        y=serie["total_facturado"],
        mode="lines+markers",
        name="Histórico",
        line=dict(color="#1f77b4", width=2),
    ))

    fig.update_layout(
        xaxis_title="Período",
        yaxis_title="Total facturado (MXN)",
        xaxis_tickangle=-45,
    )

    st.plotly_chart(fig, use_container_width=True)
    st.info("El modelo de forecasting se integrará en la siguiente fase con SageMaker.")

    # Tabla de datos históricos
    st.subheader("Serie temporal histórica")
    st.dataframe(
        serie[["periodo", "num_cfdis", "total_facturado", "iva_total"]],
        use_container_width=True,
    )