"""
app/pages/home.py
Landing page de CIFRA AI.
"""

from pathlib import Path
import streamlit as st


def show():
    # ── Hero ──────────────────────────────────────────────────────────────
    col_logo, col_text = st.columns([1, 2], gap="large")

    with col_logo:
        logo_path = Path("app/assets/logo.png")
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)

    with col_text:
        st.markdown("""
        <div style='padding-top: 1.5rem;'>
            <h1 style='font-size: 3.2rem; font-weight: 900; 
                       background: linear-gradient(135deg, #38bdf8, #2563eb);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       margin-bottom: 0.5rem;'>
                CIFRA AI
            </h1>
            <p style='font-size: 1.2rem; color: #94a3b8; 
                      font-weight: 500; margin-bottom: 1.5rem;'>
                Inteligencia Predictiva Empresarial
            </p>
            <p style='font-size: 1rem; color: #cbd5e1; line-height: 1.8;'>
                Plataforma de análisis financiero end-to-end para CFDIs.<br>
                Desde la ingesta de XMLs hasta predicciones de flujo de caja,
                todo en un solo lugar impulsado por AWS y Machine Learning.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Cards de secciones ────────────────────────────────────────────────
    st.markdown("### ¿Qué puedes hacer con CIFRA?")

    col1, col2, col3 = st.columns(3, gap="medium")

    card_style = """
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 2rem 1.5rem;
        text-align: center;
        height: 100%;
    """

    with col1:
        st.markdown(f"""
        <div style='{card_style}'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>📊</div>
            <h3 style='color: #f1f5f9; font-weight: 700; margin-bottom: 0.75rem;'>
                Dashboard
            </h3>
            <p style='color: #94a3b8; font-size: 0.95rem; line-height: 1.7;'>
                Vista ejecutiva de facturación, clientes, métodos de pago 
                y composición de CFDIs en tiempo real desde la capa Gold.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style='{card_style}'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>📤</div>
            <h3 style='color: #f1f5f9; font-weight: 700; margin-bottom: 0.75rem;'>
                Subir CFDIs
            </h3>
            <p style='color: #94a3b8; font-size: 0.95rem; line-height: 1.7;'>
                Carga y valida archivos XML de CFDI 4.0 directamente 
                al pipeline de AWS. Validación automática en tiempo real.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style='{card_style}'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>📈</div>
            <h3 style='color: #f1f5f9; font-weight: 700; margin-bottom: 0.75rem;'>
                Forecast
            </h3>
            <p style='color: #94a3b8; font-size: 0.95rem; line-height: 1.7;'>
                Predicciones de ingresos, egresos e IVA para los próximos 
                3 meses usando Random Forest con series temporales.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Pipeline ──────────────────────────────────────────────────────────
    st.markdown("### Arquitectura del pipeline")

    st.markdown("""
    <div style='background: linear-gradient(135deg, #1e293b, #0f172a);
                border: 1px solid rgba(148,163,184,0.18);
                border-radius: 18px; padding: 2rem;
                text-align: center;'>
        <div style='display: flex; justify-content: center; 
                    align-items: center; gap: 1rem; flex-wrap: wrap;'>
            <div style='background: rgba(37,99,235,0.2); border: 1px solid #2563eb;
                        border-radius: 12px; padding: 0.75rem 1.25rem;
                        color: #38bdf8; font-weight: 700;'>
                📄 CFDI XML
            </div>
            <div style='color: #475569; font-size: 1.5rem;'>→</div>
            <div style='background: rgba(217,119,6,0.2); border: 1px solid #d97706;
                        border-radius: 12px; padding: 0.75rem 1.25rem;
                        color: #fbbf24; font-weight: 700;'>
                🥉 Bronze
            </div>
            <div style='color: #475569; font-size: 1.5rem;'>→</div>
            <div style='background: rgba(100,116,139,0.2); border: 1px solid #64748b;
                        border-radius: 12px; padding: 0.75rem 1.25rem;
                        color: #cbd5e1; font-weight: 700;'>
                🥈 Silver
            </div>
            <div style='color: #475569; font-size: 1.5rem;'>→</div>
            <div style='background: rgba(234,179,8,0.2); border: 1px solid #eab308;
                        border-radius: 12px; padding: 0.75rem 1.25rem;
                        color: #fde047; font-weight: 700;'>
                🥇 Gold
            </div>
            <div style='color: #475569; font-size: 1.5rem;'>→</div>
            <div style='background: rgba(168,85,247,0.2); border: 1px solid #a855f7;
                        border-radius: 12px; padding: 0.75rem 1.25rem;
                        color: #d8b4fe; font-weight: 700;'>
                🤖 ML
            </div>
            <div style='color: #475569; font-size: 1.5rem;'>→</div>
            <div style='background: rgba(16,185,129,0.2); border: 1px solid #10b981;
                        border-radius: 12px; padding: 0.75rem 1.25rem;
                        color: #6ee7b7; font-weight: 700;'>
                📊 Dashboard
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stack tecnológico ─────────────────────────────────────────────────
    st.markdown("### Stack tecnológico")

    tech_cols = st.columns(6, gap="small")
    techs = [
        ("☁️", "AWS S3"),
        ("⚙️", "AWS Glue"),
        ("🔍", "Athena"),
        ("🐍", "Python"),
        ("🤖", "Scikit-learn"),
        ("🚀", "Streamlit"),
    ]

    for col, (icon, name) in zip(tech_cols, techs):
        col.markdown(f"""
        <div style='background: rgba(30,41,59,0.8);
                    border: 1px solid rgba(148,163,184,0.15);
                    border-radius: 12px; padding: 1rem 0.5rem;
                    text-align: center;'>
            <div style='font-size: 1.8rem;'>{icon}</div>
            <div style='color: #94a3b8; font-size: 0.8rem; 
                        font-weight: 600; margin-top: 0.5rem;'>{name}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #475569; font-size: 0.85rem;
                border-top: 1px solid rgba(148,163,184,0.12); padding-top: 1.5rem;'>
        Desarrollado por <strong style='color: #94a3b8;'>Manuel De la Tejera & Andrés Padrón</strong>
        · ITAM MCD 2026 · 
        <strong style='color: #94a3b8;'>CIFRA AI</strong> — Inteligencia Predictiva Empresarial
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    show()