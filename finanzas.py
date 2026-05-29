import streamlit as st
import os

# --- ARCHIVO BASE DE DATOS DE USUARIOS ---
ARCHIVO_USUARIOS = "usuarios_db.txt"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Finanzas Pro", page_icon="💰", layout="centered")

# --- MENÚ LATERAL (SIDEBAR) - CONTROL DE SESIÓN Y TEMA ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>🎨 Apariencia</h2>", unsafe_allow_html=True)
    # Selector de modo de color
    tema = st.radio("Elige el estilo visual:", ["Modo Claro ☀️", "Modo Oscuro 🌙"], label_visibility="collapsed")
    st.write("---")

# --- DISEÑO VISUAL ADAPTATIVO (CSS DINÁMICO) ---
if tema == "Modo Oscuro 🌙":
    color_fondo = "#121212"
    color_texto = "#e0e0e0"
    color_tarjeta = "linear-gradient(135deg, #1f4068 0%, #162447 100%)"
    color_item_historial = "#1b1b1b"
    color_borde = "#333333"
else:
    color_fondo = "#f8f9fa"
    color_texto = "#212529"
    color_tarjeta = "linear-gradient(135deg, #1d3557 0%, #457b9d 100%)"
    color_item_historial = "#ffffff"
    color_borde = "#e9ecef"

st.markdown(
    f"""
    <style>
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}} .stAppDeployButton {{display:none;}}
    
    /* Configuración del fondo total */
    .stApp {{
        background-color: {color_fondo} !important;
        color: {color_texto} !important;
    }}
    
    /* Textos globales adaptativos */
    h1, h2, h3, h4, p, label, .stMarkdown {{
        color: {color_texto} !important;
    }}
    
    /* Tarjeta del Saldo Principal */
    .tarjeta-saldo {{
        background: {color_tarjeta};
        color: white !important;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0px 10px 25px rgba(0, 0, 0, 0.15);
        text-align: center;
        margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    .tarjeta-saldo h3 {{
        margin: 0 !important;
        font-size: 0.95rem !important;
        letter-spacing: 1.5px;
        opacity: 0.85;
        color: #f1faee !important;
    }}
    .tarjeta-saldo h1 {{
        margin: 10px 0 0 0 !important;
        font-size: 2.6rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }}
    
    /* Bloques del historial elegantes */
    .item-historial {{
        background-color: {color_item_historial};
