import streamlit as st
import os

# --- ARCHIVO BASE DE DATOS DE USUARIOS ---
ARCHIVO_USUARIOS = "usuarios_db.txt"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Finanzas Pro", page_icon="💰", layout="centered")

# --- MENÚ LATERAL (SIDEBAR) - CONTROL DE SESIÓN Y TEMA ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>🎨 Apariencia</h2>", unsafe_allow_html=True)
    tema = st.radio("Elige el estilo visual:", ["Modo Claro ☀️", "Modo Oscuro 🌙"], label_visibility="collapsed")
    st.write("---")

# --- DISEÑO VISUAL ADAPTATIVO (CSS FIJO SIN F-STRING) ---
# Escondemos menús nativos y aplicamos estilos base comunes
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} .stAppDeployButton {display:none;}
    
    .tarjeta-saldo {
        color: white !important;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0px 10px 25px rgba(0, 0, 0, 0.15);
        text-align: center;
        margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .tarjeta-saldo h3 {
        margin: 0 !important;
        font-size: 0.95rem !important;
        letter-spacing: 1.5px;
        opacity: 0.85;
        color: #f1faee !important;
    }
    .tarjeta-saldo h1 {
        margin: 10px 0 0 0 !important;
        font-size: 2.6rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    
    .item-historial {
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 6px solid #ccc;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.02);
        font-family: monospace;
        font-size: 0.95rem;
    }
    .ingreso-style { border-left-color: #2a9d8f !important; }
    .gasto-style { border-left-color: #e63946 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# Inyectamos solo los colores del tema seleccionado para evitar romper las llaves de Python
if tema == "Modo Oscuro 🌙":
    st.markdown(
        """
        <style>
        .stApp { background-color: #121212 !important; color: #e0e0e0 !important; }
        h1, h2, h3, h4, p, label, .stMarkdown { color: #e0e0e0 !important; }
        .tarjeta-saldo { background: linear-gradient(135deg, #1f4068 0%, #162447 100%); }
        .item-historial { background-color: #1b1b1b; color: #e0e0e0; border: 1px solid #333; }
        </style>
        """, unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        .stApp { background-color: #f8f9fa !important; color: #212529 !important; }
        h1, h2, h3, h4, p, label, .stMarkdown { color: #212529 !important; }
        .tarjeta-saldo { background
