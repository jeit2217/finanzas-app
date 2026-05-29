import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Finanzas Pro", page_icon="📱", layout="centered")

# --- CSS ULTRA OPTIMIZADO PARA MÓVIL ---
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

# --- LÓGICA ---
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
    if not texto: return 0
    limpio = texto.replace(".", "").replace(",", "").replace("$", "").strip()
    return int(limpio) if limpio.isdigit() else 0

if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
if 'val_express' not in st.session_state: st.session_state.val_express = 0

# --- LOGIN ---
if st.session_state.usuario_logeado is None:
    st.markdown("<h2 style='text-align: center; margin-top:20px; font-weight:800;'>📱 Finanzas Pro</h2>", unsafe_allow_html=True)
    opcion = st.segmented_control("Acción", ["🔑 Entrar", "📝 Registrarse"], default="🔑 Entrar")
    if opcion == "🔑 Entrar":
        u_l = st.text_input("Usuario:").lower().strip()
        p_l = st.text_input("Clave:", type="password")
        if st.button("Ingresar 🚀", use_container_width=True):
            users = cargar_usuarios()
            if u_l in users and users[u_l] == p_l:
                st.session_state.usuario_logeado = u_l
                st.rerun()
            else: st.error("Datos incorrectos.")
    else:
        u_r = st.text_input("Crear Usuario:").lower().strip()
        p_r = st.text_input("Crear Clave:", type="password")
        if st.button("Registrar Cuenta ✨", use_container_width=True):
            if u_r and p_r:
                with open(ARCHIVO_USUARIOS, "a") as f: f.write(f"{u_r},{p_r}\n")
                st.success("¡Creado! Cambia a 'Entrar'")
else:
    user = st.session_state.usuario_logeado
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu"]
    CATEGORIAS = ["Comida", "Transporte", "Rumba", "Deudas", "Hogar", "Otros"]
    
    ARCH_HIST, ARCH_DEUDAS, ARCH_METAS = f"{user}_hist.json", f"{user}_deudas_v2.json", f"{user}_metas.json"

    def cargar_datos(tipo):
        p = ARCH_HIST if tipo == "hist" else (ARCH_DEUDAS if tipo == "deudas" else ARCH_METAS)
        if os.path.exists(p):
            with open(p, "r") as f: return json.load(f)
        return [] if tipo == "hist" else {}

    def guardar_datos(tipo, d):
        p = ARCH_HIST if tipo == "hist" else (ARCH_DEUDAS if tipo == "deudas" else ARCH_METAS)
        with open(p, "w") as f: json.dump(d, f)

    saldos = {b: int(open(f"{user}_s_{b.lower()}.txt", "r").read()) if os.path.exists(f"{user}_s_{b.lower()}.txt") else 0 for b in BANCOS}
    hist, deudas, metas = cargar_datos("hist"), cargar_datos("deudas"), cargar_datos("metas")

    st.markdown(f'<div class="tarjeta-saldo"><h3>DISPONIBLE TOTAL</h3><h1>${sum(saldos.values()):,}</h1></div>', unsafe_allow_html=True)
    cols_html = "".join([f'<div class="tarjeta-banco"><p>{b}</p><h4>${saldos[b]:,}</h4></div>' for b in BANCOS])
    st.markdown(f'<div class="contenedor-bancos">{cols_html}</div>', unsafe_allow_html=True)

    tab_movs, tab_hist, tab_stats, tab_deudas, tab_metas = st.tabs(["💸 + / -", "📊 Hist", "📈 Stats", "📌 Deudas", "🎯 Metas"])

    def render_teclado_express(key_prefix):
        st.markdown("<p style='font-size:0.75rem; margin-bottom:2px; opacity:0.6;'>⚡ Teclado Rápido:</p>", unsafe_allow_html=True)
        f1, f2 = st.columns(3), st.columns(3)
        btns = [2000, 5000, 10000, 20000, 50000]
        for i, val in enumerate(btns):
            col = f1[i] if i < 3 else f2[i-3]
            if col.button(f"+${val//1000}k", key=f"{key_prefix}_{val}"): st.session_state.val_express += val
        if f2[2].button("🧹", key=f"{key_prefix}_clr"): st.session_state.val_express = 0

    with tab_movs:
        tipo_mov = st.segmented_control("Transacción", ["📉 Gasto", "📈 Ingreso", "🔄 Transf.", "🎯 Ahorro"], default="📉 Gasto")
        render_teclado_express(tipo_mov[:4])
        with st.form("fm", clear_on_submit=True):
            b_or = st.selectbox("¿Cuenta?", BANCOS)
            monto = st.text_input("Monto:", value=f"{st.session_state.val_express:,}" if st.session_state.val_express > 0 else "")
            if st.form_submit_button("Confirmar"):
                m = procesar_monto_texto(monto)
                if m > 0:
                    saldos[b_or] -= m if tipo_mov != "📈 Ingreso" else -m
                    with open(f"{user}_s_{b_or.lower()}.txt", "w") as f: f.write(str(saldos[b_or]))
                    st.session_state.val_express = 0
                    st.rerun()

    with tab_metas:
        for m_n, m_d in list(metas.items()):
            st.markdown(f"**{m_n}** (${m_d['ahorrado']:,} / ${m_d['objetivo']:,})")
            st.progress(min(m_d['ahorrado'] / m_d['objetivo'], 1.0))
            if st.button("❌ Quitar", key=f"del_{m_n}"): # ERROR CORREGIDO: Sin 'size'
                del metas[m_n]
                guardar_datos("metas", metas)
                st.rerun()

    if st.button("🚪 Cerrar Sesión"):
        st.session_state.usuario_logeado = None
        st.rerun()
