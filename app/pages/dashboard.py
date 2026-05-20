"""
app/pages/dashboard.py
Dashboard principal con análisis financiero de CFDIs.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app.utils.athena_connector import (
    get_serie_temporal,
    get_top_clientes,
    get_distribucion_tipos,
    get_distribucion_pago,
)


def show():
    st.title("Dashboard financiero")
    st.caption("Análisis de CFDIs — datos desde Gold layer")

    # ── Cargar datos ───────────────────────────────────────────────────────
    with st.spinner("Cargando datos..."):
        serie     = get_serie_temporal()
        clientes  = get_top_clientes()
        tipos     = get_distribucion_tipos()
        pagos     = get_distribucion_pago()

    # ── KPIs ───────────────────────────────────────────────────────────────
    ingresos = serie[serie["year"] >= 2024]["total_facturado"].sum()
    num_cfdis = serie["num_cfdis"].sum()
    ticket_prom = serie["total_facturado"].sum() / num_cfdis

    col1, col2, col3 = st.columns(3)
    col1.metric("Total facturado", f"${serie['total_facturado'].sum():,.0f}")
    col2.metric("Total CFDIs",     f"{num_cfdis:,}")
    col3.metric("Ticket promedio", f"${ticket_prom:,.0f}")

    st.markdown("---")

    # ── Serie temporal ─────────────────────────────────────────────────────
    st.subheader("Ingresos mensuales")
    fig = px.bar(
        serie,
        x="periodo",
        y="total_facturado",
        labels={"periodo": "Período", "total_facturado": "Total facturado (MXN)"},
        color_discrete_sequence=["#1f77b4"],
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # ── Dos columnas ───────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Top 10 clientes")
        fig2 = px.bar(
            clientes.head(10),
            x="total_facturado",
            y="nombre_receptor",
            orientation="h",
            labels={"total_facturado": "Total (MXN)", "nombre_receptor": "Cliente"},
            color_discrete_sequence=["#2ca02c"],
        )
        fig2.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.subheader("Distribución por tipo")
        fig3 = px.pie(
            tipos,
            values="total_facturado",
            names="tipo_nombre",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── Método de pago ─────────────────────────────────────────────────────
    st.subheader("Distribución por método de pago")
    fig4 = px.bar(
        pagos,
        x="metodo_pago",
        y="total_facturado",
        color="forma_pago",
        labels={"total_facturado": "Total (MXN)", "metodo_pago": "Método"},
        barmode="group",
    )
    st.plotly_chart(fig4, use_container_width=True)