"""
app/main.py
Entry point de la app CIFRA AI en Streamlit.
"""

from pathlib import Path

import streamlit as st
from streamlit_option_menu import option_menu


st.set_page_config(
    page_title="CIFRA AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css() -> None:
    """Load custom CSS styles."""
    css_path = Path("app/styles/custom.css")
    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text()}</style>",
            unsafe_allow_html=True,
        )


load_css()


with st.sidebar:
    st.image("app/assets/logo.png", use_container_width=True)
    st.caption("Inteligencia predictiva empresarial")
    st.markdown("---")

    page = option_menu(
    menu_title="Navegación",
    options=["Home", "Dashboard", "Subir CFDIs", "Forecast"],
    icons=["house", "bar-chart-line", "cloud-upload", "graph-up-arrow"],
    menu_icon="grid",
    default_index=0,
        styles={
            "container": {
                "padding": "0.45rem",
                "background-color": "rgba(15, 23, 42, 0.65)",
                "border": "1px solid rgba(148, 163, 184, 0.18)",
                "border-radius": "18px",
            },
            "icon": {
                "color": "#38bdf8",
                "font-size": "18px",
            },
            "nav-link": {
                "font-size": "15px",
                "font-weight": "500",
                "text-align": "left",
                "margin": "6px 4px",
                "padding": "12px 14px",
                "border-radius": "14px",
                "color": "#cbd5e1",
                "--hover-color": "rgba(37, 99, 235, 0.22)",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #2563eb 0%, #06b6d4 100%)",
                "color": "#ffffff",
                "font-weight": "700",
            },
            "menu-title": {
                "font-size": "13px",
                "font-weight": "700",
                "color": "#94a3b8",
                "letter-spacing": "0.08em",
                "text-transform": "uppercase",
                "padding": "12px 16px 4px 16px",
            },
        },
    )

    st.markdown("---")
    st.caption("Bronze → Silver → Gold → ML")


if page == "Home":
    from app.pages import home
    home.show()
elif page == "Dashboard":
    from app.pages import dashboard
    dashboard.show()
elif page == "Subir CFDIs":
    from app.pages import upload
    upload.show()
elif page == "Forecast":
    from app.pages import forecast
    forecast.show()