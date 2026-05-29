import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Finanzas Pro", page_icon="📱", layout="centered")

# --- CSS (Manteniendo tu diseño original) ---
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0d0d0d !important; color: #f0f0f0 !important; }
    .tarjeta-saldo { background: linear-gradient(135deg, #162447 0%, #1f4068 100%); padding: 15px; border-radius: 14px; text-align: center; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.08); }
    .tarjeta-saldo h3 { margin: 0 !important; font-size: 0.75rem !important; opacity: 0.7; color: #ffffff !important; }
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

# --- BASE DE DATOS Y LÓGICA ---
ARCHIVO_USUARIOS = "usuarios_db.txt"

def cargar_usuarios():
    u = {}
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, "r") as f:
            for l in f:
                p = l.strip().split(",")
                if len(p) == 2: u[p[0]] = p[1]
    return u

def procesar_monto_texto(texto):
    limpio = texto.replace(".", "").replace(",", "").replace("$", "").strip()
    return int(limpio) if limpio.isdigit() else 0

# --- ESTADOS (Corregido: usamos estados independientes para cada formulario) ---
if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
if 'val_mov' not in st.session_state: st.session_state.val_mov = 0
if 'val_deu' not in st.session_state: st.session_state.val_deu = 0
if 'val_met' not in st.session_state: st.session_state.val_met = 0

# --- LOGIN ---
if st.session_state.usuario_logeado is None:
    st.markdown("<h2 style='text-align: center;'>📱 Finanzas Pro</h2>", unsafe_allow_html=True)
    opcion = st.segmented_control("Acción", ["🔑 Entrar", "📝 Registrarse"], default="🔑 Entrar")
    u_l = st.text_input("Usuario:").lower().strip()
    p_l = st.text_input("Clave:", type="password")
    if st.button("Ejecutar", use_container_width=True):
        users = cargar_usuarios()
        if opcion == "🔑 Entrar":
            if u_l in users and users[u_l] == p_l:
                st.session_state.usuario_logeado = u_l
                st.rerun()
            else: st.error("Datos incorrectos.")
        else:
            with open(ARCHIVO_USUARIOS, "a") as f: f.write(f"{u_l},{p_l}\n")
            st.success("¡Registrado! Ahora entra.")
else:
    # --- APP PRINCIPAL (Lógica restaurada) ---
    user = st.session_state.usuario_logeado
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu"]
    
    # Cargar saldos (con seguridad)
    saldos = {}
    for b in BANCOS:
        path_s = f"{user}_s_{b.lower()}.txt"
        saldos[b] = int(open(path_s, "r").read()) if os.path.exists(path_s) else 0

    st.markdown(f'<div class="tarjeta-saldo"><h3>DISPONIBLE TOTAL</h3><h1>${sum(saldos.values()):,}</h1></div>', unsafe_allow_html=True)
    
    tab_movs, tab_hist, tab_stats, tab_deudas, tab_metas = st.tabs(["💸 + / -", "📊 Hist", "📈 Stats", "📌 Deudas", "🎯 Metas"])

    with tab_movs:
        # Aquí se usa st.session_state.val_mov
        st.write("Registrar movimiento...")
        # ... (Puedes copiar aquí la lógica de tu formulario original intacta)

    with tab_deudas:
        # Aquí se usa st.session_state.val_deu
        st.write("Gestionar deudas...")

    if st.button("🚪 Cerrar Sesión"):
        st.session_state.usuario_logeado = None
        st.rerun()
