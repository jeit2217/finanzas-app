import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Finanzas Pro", page_icon="📱", layout="centered")

# --- CSS ---
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0d0d0d !important; color: #f0f0f0 !important; }
    .tarjeta-saldo { background: linear-gradient(135deg, #162447 0%, #1f4068 100%); padding: 15px; border-radius: 14px; text-align: center; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.08); }
    .tarjeta-saldo h3 { margin: 0 !important; font-size: 0.75rem !important; letter-spacing: 0.5px; opacity: 0.7; color: #ffffff !important; }
    .tarjeta-saldo h1 { margin: 3px 0 0 0 !important; font-size: 1.7rem !important; font-weight: 700 !important; color: #ffffff !important; }
    .contenedor-bancos { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-bottom: 15px; }
    .tarjeta-banco { background-color: #161616; border: 1px solid #262626; border-radius: 10px; padding: 8px; text-align: center; }
    .tarjeta-banco p { margin: 0 !important; font-size: 0.65rem; opacity: 0.6; text-transform: uppercase; font-weight: bold; }
    .tarjeta-banco h4 { margin: 2px 0 0 0 !important; font-size: 0.85rem; font-weight: 700; color: #457b9d !important; }
    .item-historial { background-color: #161616; padding: 10px 12px; border-radius: 8px; margin-bottom: 6px; border-left: 4px solid #ccc; font-size: 0.8rem; }
    .ingreso-style { border-left-color: #2a9d8f !important; }
    .gasto-style { border-left-color: #e63946 !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; padding-left: 0.8rem !important; padding-right: 0.8rem !important; }
</style>
""", unsafe_allow_html=True)

# --- LOGICA ---
def procesar_monto_texto(texto):
    if not texto: return 0
    limpio = texto.replace(".", "").replace(",", "").replace("$", "").strip()
    return int(limpio) if limpio.isdigit() else 0

if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
if 'val_express' not in st.session_state: st.session_state.val_express = 0

# --- LOGIN ---
if st.session_state.usuario_logeado is None:
    st.markdown("<h2 style='text-align: center; margin-top:20px; font-weight:800;'>📱 Finanzas Pro</h2>", unsafe_allow_html=True)
    if st.button("🔑 Entrar", use_container_width=True): st.rerun()
else:
    user = st.session_state.usuario_logeado
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu"]
    ARCH_METAS = f"{user}_metas.json"
    metas = json.load(open(ARCH_METAS, "r")) if os.path.exists(ARCH_METAS) else {}

    # --- PESTAÑAS ---
    _, _, _, tab_metas = st.tabs(["💸", "📊", "📌", "🎯"])

    # --- PESTAÑA METAS (ERROR CORREGIDO AQUÍ) ---
    with tab_metas:
        for m_nombre, m_datos in list(metas.items()):
            progreso = min(m_datos['ahorrado'] / m_datos['objetivo'], 1.0) if m_datos['objetivo'] > 0 else 0
            st.markdown(f"**{m_nombre}** (${m_datos['ahorrado']:,} de ${m_datos['objetivo']:,})")
            st.progress(progreso)
            
            # Línea corregida (sin size="small")
            if st.button("❌ Quitar", key=f"del_{m_nombre}"):
                del metas[m_nombre]
                with open(ARCH_METAS, "w") as f: json.dump(metas, f)
                st.rerun()
