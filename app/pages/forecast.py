from __future__ import annotations

import awswrangler as wr
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.utils.athena_connector import get_serie_temporal_completa

FORECAST_S3 = "s3://cifra-datalake-dev/ml/forecast/forecast_next_3_months.csv"


def load_forecast() -> pd.DataFrame:
    try:
        df = wr.s3.read_csv(FORECAST_S3)
        for col in ["forecast", "total_ingresos", "total_egresos", "iva_total"]:
            df[col] = df[col].round(2)
        return df
    except Exception:
        return pd.DataFrame(columns=["periodo", "forecast",
                                     "total_ingresos", "total_egresos", "iva_total"])


def show():
    st.title("Forecast financiero")
    st.caption("Predicción de ingresos, egresos e IVA para los próximos 3 meses")

    with st.spinner("Cargando serie temporal y predicciones..."):
        serie    = get_serie_temporal_completa()
        forecast = load_forecast()

    # ── KPIs ──────────────────────────────────────────────────────────────
    if not forecast.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Forecast total",    f"${forecast['forecast'].iloc[0]:,.0f}")
        col2.metric("Forecast ingresos", f"${forecast['total_ingresos'].iloc[0]:,.0f}")
        col3.metric("Forecast egresos",  f"${forecast['total_egresos'].iloc[0]:,.0f}")
        col4.metric("Forecast IVA",      f"${forecast['iva_total'].iloc[0]:,.0f}")

    st.markdown("---")

    # ── Gráfica ingresos vs egresos histórico + forecast ──────────────────
    st.subheader("Ingresos vs Egresos")
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=serie["periodo"], y=serie["total_ingresos"],
        mode="lines+markers", name="Ingresos histórico",
        line=dict(color="#38bdf8", width=2),
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=serie["periodo"], y=serie["total_egresos"],
        mode="lines+markers", name="Egresos histórico",
        line=dict(color="#f43f5e", width=2),
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))

    if not forecast.empty:
        fig.add_trace(go.Scatter(
            x=forecast["periodo"], y=forecast["total_ingresos"],
            mode="lines+markers", name="Forecast ingresos",
            line=dict(color="#38bdf8", width=2, dash="dash"),
            marker=dict(size=10, symbol="diamond"),
            hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=forecast["periodo"], y=forecast["total_egresos"],
            mode="lines+markers", name="Forecast egresos",
            line=dict(color="#f43f5e", width=2, dash="dash"),
            marker=dict(size=10, symbol="diamond"),
            hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
        ))

    fig.update_layout(
        xaxis_title="Periodo", yaxis_title="MXN",
        xaxis_tickangle=-45, height=460,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(148,163,184,0.1)"),
        yaxis=dict(gridcolor="rgba(148,163,184,0.1)"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Gráfica IVA histórico + forecast ──────────────────────────────────
    st.subheader("IVA trasladado")
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=serie["periodo"], y=serie["iva_total"],
        mode="lines+markers", name="IVA histórico",
        line=dict(color="#a855f7", width=2),
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))

    if not forecast.empty:
        fig2.add_trace(go.Scatter(
            x=forecast["periodo"], y=forecast["iva_total"],
            mode="lines+markers", name="Forecast IVA",
            line=dict(color="#a855f7", width=2, dash="dash"),
            marker=dict(size=10, symbol="diamond"),
            hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
        ))

    fig2.update_layout(
        xaxis_title="Periodo", yaxis_title="MXN",
        xaxis_tickangle=-45, height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(148,163,184,0.1)"),
        yaxis=dict(gridcolor="rgba(148,163,184,0.1)"),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Tabla forecast ────────────────────────────────────────────────────
    if not forecast.empty:
        st.subheader("Predicciones generadas")
        display = forecast.copy()
        for col in ["forecast", "total_ingresos", "total_egresos", "iva_total"]:
            display[col] = display[col].apply(lambda x: f"${x:,.0f}")
        display = display.rename(columns={
            "periodo":        "Período",
            "forecast":       "Total",
            "total_ingresos": "Ingresos",
            "total_egresos":  "Egresos",
            "iva_total":      "IVA",
        })
        st.dataframe(display, use_container_width=True, hide_index=True)

        if forecast["total_ingresos"].iloc[-1] < forecast["total_ingresos"].iloc[0]:
            st.warning("El modelo proyecta una disminución en ingresos durante el horizonte.")
        else:
            st.success("El modelo proyecta estabilidad o crecimiento en ingresos.")


if __name__ == "__main__":
    show()