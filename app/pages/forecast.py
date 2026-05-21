from __future__ import annotations

import awswrangler as wr
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.utils.athena_connector import get_serie_temporal

FORECAST_S3 = "s3://cifra-datalake-dev/ml/forecast/forecast_next_3_months.csv"


def load_forecast() -> pd.DataFrame:
    try:
        df = wr.s3.read_csv(FORECAST_S3)
        df["forecast"] = df["forecast"].round(2)
        return df
    except Exception:
        return pd.DataFrame(columns=["periodo", "forecast"])


def show():
    st.title("Forecast financiero")
    st.caption("Predicción de ingresos facturados para los próximos 3 meses")

    with st.spinner("Cargando serie temporal y predicciones..."):
        serie = get_serie_temporal()
        forecast = load_forecast()

    total_actual = serie["total_facturado"].iloc[-1]
    forecast_1m = forecast["forecast"].iloc[0] if not forecast.empty else None

    col1, col2, col3 = st.columns(3)
    col1.metric("Último ingreso mensual", f"${total_actual:,.0f}")

    if forecast_1m is not None:
        cambio = ((forecast_1m - total_actual) / total_actual) * 100
        col2.metric("Forecast próximo mes", f"${forecast_1m:,.0f}", f"{cambio:,.1f}%")
        col3.metric("Horizonte", "3 meses")
    else:
        col2.metric("Forecast próximo mes", "No disponible")
        col3.metric("Horizonte", "No disponible")

    st.markdown("---")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=serie["periodo"],
            y=serie["total_facturado"],
            mode="lines+markers",
            name="Histórico",
        )
    )

    if not forecast.empty:
        fig.add_trace(
            go.Scatter(
                x=forecast["periodo"],
                y=forecast["forecast"],
                mode="lines+markers",
                name="Forecast",
                line=dict(dash="dash"),
            )
        )

    fig.update_layout(
        title="Histórico y forecast de ingresos",
        xaxis_title="Periodo",
        yaxis_title="Total facturado (MXN)",
        xaxis_tickangle=-45,
    )

    st.plotly_chart(fig, use_container_width=True)

    if not forecast.empty:
        st.subheader("Predicciones generadas")
        st.dataframe(forecast, use_container_width=True)

        if forecast["forecast"].iloc[-1] < forecast["forecast"].iloc[0]:
            st.warning(
                "Alerta: el modelo proyecta una disminución en los ingresos "
                "durante el horizonte de predicción."
            )
        else:
            st.success(
                "El modelo proyecta estabilidad o crecimiento en los ingresos "
                "durante el horizonte de predicción."
            )
    else:
        st.info(
            "Todavía no existe un archivo de predicciones. Ejecuta: "
            "`python -m ml.inference.predict`."
        )

    st.subheader("Serie temporal histórica")
    st.dataframe(
        serie[["periodo", "num_cfdis", "total_facturado", "iva_total"]],
        use_container_width=True,
    )


if __name__ == "__main__":
    show()