"""
app/pages/home.py
Landing page de CIFRA AI.
"""

import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


def _img_b64(path: str) -> str:
    p = Path(path)
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return ""


def show():
    logo_b64 = _img_b64("app/assets/logo.png")

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='display: flex; align-items: center; gap: 3rem;
                padding: 2.5rem 0 1.5rem 0;'>
        <div style='flex-shrink: 0;'>
            <img src="data:image/png;base64,{logo_b64}"
                 style='width: 280px; max-width: 100%;'>
        </div>
        <div>
            <h1 style='font-size: 3.5rem; font-weight: 900; margin: 0 0 0.4rem 0;
                       background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       line-height: 1.1;'>
                CIFRA AI
            </h1>
            <p style='font-size: 1.15rem; color: #64748b; font-weight: 600;
                      letter-spacing: 0.06em; text-transform: uppercase;
                      margin: 0 0 1.2rem 0;'>
                Inteligencia Predictiva Empresarial
            </p>
            <p style='font-size: 1.05rem; color: #94a3b8; line-height: 1.85;
                      max-width: 520px; margin: 0;'>
                Plataforma end-to-end para análisis financiero de CFDIs —
                desde la ingesta de XMLs hasta predicciones de flujo de caja,
                impulsada por AWS y Machine Learning.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='height: 1px; background: linear-gradient(90deg,
        transparent, rgba(56,189,248,0.4), rgba(37,99,235,0.4), transparent);
        margin: 0.5rem 0 2.5rem 0;'></div>
    """, unsafe_allow_html=True)

    # ── Cards ─────────────────────────────────────────────────────────────
    st.markdown("""
    <p style='font-size: 0.8rem; font-weight: 700; color: #38bdf8;
              letter-spacing: 0.12em; text-transform: uppercase;
              margin-bottom: 0.5rem;'>MÓDULOS</p>
    <h2 style='font-size: 1.8rem; font-weight: 800; color: #f1f5f9;
               margin: 0 0 1.8rem 0;'>¿Qué puedes hacer con CIFRA?</h2>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")

    cards = [
        {
            "accent": "#38bdf8",
            "accent_bg": "rgba(56,189,248,0.08)",
            "icon": """<svg width="32" height="32" viewBox="0 0 24 24" fill="none"
                stroke="#38bdf8" stroke-width="2" stroke-linecap="round">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <path d="M3 9h18M9 21V9"/>
                <polyline points="7,15 10,12 13,14 17,10"/>
            </svg>""",
            "title": "Dashboard",
            "desc": "Vista ejecutiva de facturación, clientes y composición de CFDIs en tiempo real desde la capa Gold de S3.",
        },
        {
            "accent": "#06b6d4",
            "accent_bg": "rgba(6,182,212,0.08)",
            "icon": """<svg width="32" height="32" viewBox="0 0 24 24" fill="none"
                stroke="#06b6d4" stroke-width="2" stroke-linecap="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>""",
            "title": "Subir CFDIs",
            "desc": "Carga y valida archivos XML de CFDI 4.0 al pipeline de AWS con validación automática en tiempo real.",
        },
        {
            "accent": "#a855f7",
            "accent_bg": "rgba(168,85,247,0.08)",
            "icon": """<svg width="32" height="32" viewBox="0 0 24 24" fill="none"
                stroke="#a855f7" stroke-width="2" stroke-linecap="round">
                <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
                <polyline points="16 7 22 7 22 13"/>
            </svg>""",
            "title": "Forecast",
            "desc": "Predicciones de ingresos, egresos e IVA para los próximos 3 meses con Random Forest y series temporales.",
        },
    ]

    for col, card in zip([col1, col2, col3], cards):
        col.markdown(f"""
        <div style='background: linear-gradient(145deg, #1e293b, #0f172a);
                    border: 1px solid rgba(148,163,184,0.12);
                    border-top: 2px solid {card["accent"]};
                    border-radius: 16px; padding: 2rem 1.75rem;
                    height: 100%; transition: all 0.2s;'>
            <div style='background: {card["accent_bg"]};
                        border-radius: 12px; padding: 0.75rem;
                        display: inline-block; margin-bottom: 1.25rem;'>
                {card["icon"]}
            </div>
            <h3 style='color: #f1f5f9; font-weight: 700; font-size: 1.15rem;
                       margin: 0 0 0.75rem 0;'>{card["title"]}</h3>
            <p style='color: #64748b; font-size: 0.92rem; line-height: 1.75;
                      margin: 0;'>{card["desc"]}</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Pipeline ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <p style='font-size: 0.8rem; font-weight: 700; color: #38bdf8;
              letter-spacing: 0.12em; text-transform: uppercase;
              margin-bottom: 0.5rem;'>ARQUITECTURA</p>
    <h2 style='font-size: 1.8rem; font-weight: 800; color: #f1f5f9;
               margin: 0 0 1.5rem 0;'>Pipeline de datos</h2>
    """, unsafe_allow_html=True)

    components.html("""
    <div style="background: linear-gradient(145deg, #1e293b, #0f172a);
                border: 1px solid rgba(148,163,184,0.12);
                border-radius: 16px; padding: 2rem;
                display: flex; align-items: center;
                justify-content: center; gap: 0.75rem; flex-wrap: wrap;
                font-family: sans-serif;">

        <div style="text-align:center; padding: 0.75rem 1.25rem;
                    background: rgba(37,99,235,0.12); border: 1px solid #2563eb;
                    border-radius: 12px; min-width: 85px;">
            <div style="color:#93c5fd; font-weight:800; font-size:0.85rem;">XML</div>
            <div style="color:#2563eb; font-size:0.7rem; margin-top:3px;">CFDI 4.0</div>
        </div>
        <div style="color:#475569; font-size:1.4rem;">→</div>

        <div style="text-align:center; padding: 0.75rem 1.25rem;
                    background: rgba(217,119,6,0.12); border: 1px solid #d97706;
                    border-radius: 12px; min-width: 85px;">
            <div style="color:#fcd34d; font-weight:800; font-size:0.85rem;">Bronze</div>
            <div style="color:#d97706; font-size:0.7rem; margin-top:3px;">Raw S3</div>
        </div>
        <div style="color:#475569; font-size:1.4rem;">→</div>

        <div style="text-align:center; padding: 0.75rem 1.25rem;
                    background: rgba(100,116,139,0.12); border: 1px solid #64748b;
                    border-radius: 12px; min-width: 85px;">
            <div style="color:#cbd5e1; font-weight:800; font-size:0.85rem;">Silver</div>
            <div style="color:#64748b; font-size:0.7rem; margin-top:3px;">Parquet</div>
        </div>
        <div style="color:#475569; font-size:1.4rem;">→</div>

        <div style="text-align:center; padding: 0.75rem 1.25rem;
                    background: rgba(202,138,4,0.12); border: 1px solid #ca8a04;
                    border-radius: 12px; min-width: 85px;">
            <div style="color:#fde68a; font-weight:800; font-size:0.85rem;">Gold</div>
            <div style="color:#ca8a04; font-size:0.7rem; margin-top:3px;">Agregados</div>
        </div>
        <div style="color:#475569; font-size:1.4rem;">→</div>

        <div style="text-align:center; padding: 0.75rem 1.25rem;
                    background: rgba(124,58,237,0.12); border: 1px solid #7c3aed;
                    border-radius: 12px; min-width: 85px;">
            <div style="color:#c4b5fd; font-weight:800; font-size:0.85rem;">ML</div>
            <div style="color:#7c3aed; font-size:0.7rem; margin-top:3px;">Forecast</div>
        </div>
        <div style="color:#475569; font-size:1.4rem;">→</div>

        <div style="text-align:center; padding: 0.75rem 1.25rem;
                    background: rgba(5,150,105,0.12); border: 1px solid #059669;
                    border-radius: 12px; min-width: 85px;">
            <div style="color:#6ee7b7; font-weight:800; font-size:0.85rem;">App</div>
            <div style="color:#059669; font-size:0.7rem; margin-top:3px;">Dashboard</div>
        </div>

    </div>
    """, height=160)

    # ── Stack ─────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <p style='font-size: 0.8rem; font-weight: 700; color: #38bdf8;
              letter-spacing: 0.12em; text-transform: uppercase;
              margin-bottom: 0.5rem;'>TECNOLOGÍA</p>
    <h2 style='font-size: 1.8rem; font-weight: 800; color: #f1f5f9;
               margin: 0 0 1.5rem 0;'>Stack</h2>
    """, unsafe_allow_html=True)

    techs = [
        ("#f97316", "S3", "Storage"),
        ("#38bdf8", "Glue", "ETL"),
        ("#a855f7", "Athena", "Query"),
        ("#eab308", "SageMaker", "ML"),
        ("#10b981", "Python", "Backend"),
        ("#06b6d4", "Streamlit", "Frontend"),
    ]

    cols = st.columns(6, gap="small")
    for col, (color, name, role) in zip(cols, techs):
        col.markdown(f"""
        <div style='background: rgba(30,41,59,0.6);
                    border: 1px solid rgba(148,163,184,0.1);
                    border-bottom: 2px solid {color};
                    border-radius: 12px; padding: 1.2rem 0.5rem;
                    text-align: center;'>
            <div style='color: {color}; font-weight: 800;
                        font-size: 0.95rem;'>{name}</div>
            <div style='color: #475569; font-size: 0.72rem;
                        margin-top: 4px; font-weight: 500;'>{role}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; padding-top: 1.5rem;
                border-top: 1px solid rgba(148,163,184,0.08);'>
        <p style='color: #334155; font-size: 0.82rem; margin: 0;'>
            Desarrollado por
            <strong style='color: #64748b;'>Manuel De la Tejera & Andrés Padrón</strong>
            · ITAM MCD 2026
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    show()