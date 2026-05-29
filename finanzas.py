import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN OPTIMIZADA ---
st.set_page_config(page_title="Finanzas Pro", page_icon="💰", layout="centered")

# --- CSS MÓVIL (Reducido y eficiente) ---
st.markdown("""
<style>
    .stApp { background-color: #121212 !important; color: #e0e0e0 !important; }
    #MainMenu, footer, header {visibility: hidden;}
    .css-1544g2n {padding-top: 1rem !important;}
    div.stButton > button { border-radius: 8px !important; font-size: 0.85rem !important; height: 38px !important; }
    .tarjeta-saldo, .tarjeta-gastos { padding: 15px !important; border-radius: 12px !important; text-align: center; margin-bottom: 10px !important; }
    .tarjeta-saldo h1 { font-size: 1.6rem !important; margin: 0 !important; }
    .tarjeta-gastos h1 { font-size: 1.4rem !important; margin: 0 !important; }
    .contenedor-bancos { display: grid; grid-template-columns: repeat(2, 1fr); gap: 5px; margin-bottom: 10px; }
    .tarjeta-banco { background-color: #1b1b1b; border-radius: 8px; padding: 5px; text-align: center; }
    .tarjeta-banco p { font-size: 0.6rem !important; margin: 0 !important; }
    .tarjeta-banco h4 { font-size: 0.8rem !important; margin: 0 !important; color: #457b9d !important; }
    .item-historial { font-size: 0.8rem !important; padding: 8px !important; margin-bottom: 5px !important; border-left: 4px solid #ccc; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES BASE ---
def cargar_usuarios():
    u = {}
    if os.path.exists("usuarios_db.txt"):
        with open("usuarios_db.txt", "r") as f:
            for l in f:
                p = l.strip().split(",")
                if len(p) == 2: u[p[0]] = p[1]
    return u

def procesar_monto_texto(texto):
    limpio = texto.replace(".", "").replace(",", "").replace("$", "").strip()
    return int(limpio) if limpio.isdigit() else 0

# --- ESTADO ---
if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
# (Simplificado: inicialización de estados exprés omitida por brevedad, se mantiene la lógica original)
for key in ['val_express_ing', 'val_express_gas', 'val_express_met', 'val_express_tra', 'val_express_deu', 'val_express_mcrear']:
    if key not in st.session_state: st.session_state[key] = 0

# --- LÓGICA DE TECLADO MÓVIL ---
def render_teclado(key_prefix):
    st.caption("⚡ Teclado Rápido:")
    cols = st.columns(6)
    valores = [2000, 5000, 10000, 20000, 50000, 100000]
    for i, val in enumerate(valores):
        if cols[i].button(f"{val//1000}k", key=f"{key_prefix}_{val}"):
            st.session_state[f"val_express_{key_prefix}"] += val
    if st.button("🧹 Borrar", key=f"{key_prefix}_clr", use_container_width=True):
        st.session_state[f"val_express_{key_prefix}"] = 0

# --- LOGIN Y APP (Estructura lógica igual) ---
# [El resto de tu lógica se mantiene idéntica, solo reemplaza los bloques de "Teclado" 
#  por llamadas a la función render_teclado para mantener el código más corto y ordenado]

if st.session_state.usuario_logeado is None:
    # (Mantener tu lógica de login)
    pass
else:
    # (Mantener tu lógica de aplicación)
    # Ejemplo de uso en sección Ingresos:
    # render_teclado("ing")
    # ... resto de tu código ...
    pass
