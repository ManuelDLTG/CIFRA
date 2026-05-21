"""
app/pages/dashboard.py
Dashboard principal con análisis financiero de CFDIs.
"""

import plotly.express as px
import streamlit as st

from app.utils.athena_connector import (
    get_distribucion_pago,
    get_distribucion_tipos,
    get_serie_temporal,
    get_top_clientes,
)


def format_money(value: float) -> str:
    """Format numeric values as MXN currency."""
    return f"${value:,.0f}"


def show():
    st.title("Dashboard financiero")
    st.caption(
        "Vista ejecutiva de facturación, clientes, métodos de pago y composición "
        "de CFDIs a partir de la capa Gold."
    )

    with st.spinner("Cargando métricas financieras desde S3 Gold..."):
        serie = get_serie_temporal()
        clientes = get_top_clientes()
        tipos = get_distribucion_tipos()
        pagos = get_distribucion_pago()

    total_facturado = serie["total_facturado"].sum()
    num_cfdis = serie["num_cfdis"].sum()
    ticket_promedio = total_facturado / num_cfdis
    ultimo_mes = serie.iloc[-1]
    promedio_mensual = serie["total_facturado"].mean()

    st.markdown("### Resumen ejecutivo")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total facturado", format_money(total_facturado))
    col2.metric("CFDIs procesados", f"{num_cfdis:,}")
    col3.metric("Ticket promedio", format_money(ticket_promedio))
    col4.metric("Último mes", format_money(ultimo_mes["total_facturado"]))

    st.info(
        f"El pipeline consolidó **{num_cfdis:,} CFDIs** en una serie histórica de "
        f"**{len(serie)} meses**, con una facturación mensual promedio de "
        f"**{format_money(promedio_mensual)}**."
    )

    st.markdown("---")

    st.subheader("Ingresos mensuales")
    fig = px.bar(
        serie,
        x="periodo",
        y="total_facturado",
        labels={
            "periodo": "Periodo",
            "total_facturado": "Total facturado (MXN)",
        },
        text_auto=".2s",
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Total facturado: $%{y:,.0f}<extra></extra>"
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        height=460,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns([1.15, 1])

    with col_a:
        st.subheader("Top 10 clientes por facturación")
        top_10 = clientes.head(10).sort_values("total_facturado", ascending=True)

        fig_clients = px.bar(
            top_10,
            x="total_facturado",
            y="nombre_receptor",
            orientation="h",
            labels={
                "total_facturado": "Total facturado (MXN)",
                "nombre_receptor": "Cliente",
            },
            text_auto=".2s",
        )
        fig_clients.update_traces(
            hovertemplate="<b>%{y}</b><br>Total facturado: $%{x:,.0f}<extra></extra>"
        )
        fig_clients.update_layout(
            height=430,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig_clients, use_container_width=True)

    with col_b:
        st.subheader("Composición por tipo de CFDI")

        fig_tipos = px.pie(
            tipos,
            values="total_facturado",
            names="tipo_nombre",
            hole=0.45,
        )
        fig_tipos.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Total: $%{value:,.0f}<extra></extra>",
        )
        fig_tipos.update_layout(
            height=430,
            margin=dict(l=20, r=20, t=20, b=20),
            legend_title_text="Tipo",
        )
        st.plotly_chart(fig_tipos, use_container_width=True)

    st.subheader("Distribución por método y forma de pago")
    fig_pago = px.bar(
        pagos,
        x="metodo_pago",
        y="total_facturado",
        color="forma_pago",
        labels={
            "total_facturado": "Total facturado (MXN)",
            "metodo_pago": "Método de pago",
            "forma_pago": "Forma de pago",
        },
        barmode="group",
        text_auto=".2s",
    )
    fig_pago.update_traces(
        hovertemplate=(
            "<b>Método:</b> %{x}<br>"
            "Total facturado: $%{y:,.0f}<extra></extra>"
        )
    )
    fig_pago.update_layout(
        height=460,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_pago, use_container_width=True)

    st.markdown("---")
    st.caption(
        "Fuente: capa Gold generada desde CFDIs parseados en Silver y almacenados "
        "en S3 como Parquet."
    )


if __name__ == "__main__":
    show()