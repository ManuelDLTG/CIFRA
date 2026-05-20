"""
app/main.py
Entry point de la app CIFRA en Streamlit.
"""

import streamlit as st

st.set_page_config(
    page_title="CIFRA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("CIFRA")
st.sidebar.caption("CFDI Intelligence, Forecasting & Reporting Architecture")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navegación",
    ["Dashboard", "Subir CFDIs", "Forecast"],
)

if page == "Dashboard":
    from app.pages import dashboard
    dashboard.show()
elif page == "Subir CFDIs":
    from app.pages import upload
    upload.show()
elif page == "Forecast":
    from app.pages import forecast
    forecast.show()