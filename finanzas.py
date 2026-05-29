import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Finanzas Pro", page_icon="💰", layout="centered")

# --- CSS OPTIMIZADO PARA MÓVIL ---
st.markdown("""
<style>
    .stApp { background-color: #121212 !important; color: #e0e0e0 !important; padding-left: 10px !important; padding-right: 10px !important; }
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Inputs y Selectores */
    input, div[data-baseweb="select"] { background-color: #1e1e1e !important; color: white !important; font-size: 16px !important; }
    
    /* Botones */
    div.stButton > button { height: 45px !important; border-radius: 8px !important; font-weight: bold; border: none !important; }
    
    /* Tarjetas */
    .tarjeta-saldo { background: #1f4068; color: white; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; }
    .tarjeta-banco { background-color: #1b1b1b; border: 1px solid #333; border-radius: 10px; padding: 8px; text-align: center; }
    .item-historial { background-color: #1b1b1b; padding: 10px; border-radius: 8px; margin-bottom: 6px; border-left: 4px solid #ccc; font-size: 0.85rem; }
    
    /* Ajustes específicos para móviles */
    @media (max-width: 600px) {
        .stColumn { gap: 5px !important; }
        h1 { font-size: 1.5rem !important; }
        h3 { font-size: 1.1rem !important; }
    }
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
    if not texto: return 0
    limpio = texto.replace(".", "").replace(",", "").replace("$", "").strip()
    return int(limpio) if limpio.isdigit() else 0

# --- ESTADOS ---
if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
# Inicialización abreviada de estados
for s in ['val_express_ing', 'val_express_gas', 'val_express_met', 'val_express_tra', 'val_express_deu', 'val_express_mcrear']:
    if s not in st.session_state: st.session_state[s] = 0

# --- LOGIN ---
if st.session_state.usuario_logeado is None:
    st.markdown("<h1 style='text-align: center;'>📱 Finanzas Pro</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Iniciar", "📝 Registro"])
    with t1:
        u_l = st.text_input("Usuario:").lower().strip()
        p_l = st.text_input("Clave:", type="password")
        if st.button("Entrar", use_container_width=True):
            users = cargar_usuarios()
            if u_l in users and users[u_l] == p_l:
                st.session_state.usuario_logeado = u_l
                st.rerun()
            else: st.error("Datos incorrectos.")
    with t2:
        u_r = st.text_input("Nuevo Usuario:").lower().strip()
        p_r = st.text_input("Nueva Clave:", type="password")
        if st.button("Crear Cuenta", use_container_width=True):
            if u_r and p_r:
                with open(ARCHIVO_USUARIOS, "a") as f: f.write(f"{u_r},{p_r}\n")
                st.success("¡Creado!")

# --- APP PRINCIPAL ---
else:
    user = st.session_state.usuario_logeado
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu"]
    ARCH_HIST, ARCH_DEUDAS, ARCH_METAS = f"{user}_hist.json", f"{user}_deudas_v2.json", f"{user}_metas.json"

    # Funciones de carga/guardado (simplificadas)
    def cargar_datos(tipo):
        p = ARCH_HIST if tipo == "hist" else (ARCH_DEUDAS if tipo == "deudas" else ARCH_METAS)
        if os.path.exists(p):
            with open(p, "r") as f: return json.load(f)
        return [] if tipo == "hist" else {}

    def guardar_datos(tipo, d):
        p = ARCH_HIST if tipo == "hist" else (ARCH_DEUDAS if tipo == "deudas" else ARCH_METAS)
        with open(p, "w") as f: json.dump(d, f)

    def cargar_saldo(b):
        p = f"{user}_s_{b.lower()}.txt"
        return int(open(p, "r").read()) if os.path.exists(p) else 0

    def guardar_saldo(b, s):
        with open(f"{user}_s_{b.lower()}.txt", "w") as f: f.write(str(s))

    hist, deudas, metas = cargar_datos("hist"), cargar_datos("deudas"), cargar_datos("metas")
    saldos = {b: cargar_saldo(b) for b in BANCOS}

    # Interfaz Fija
    st.markdown(f'<div class="tarjeta-saldo"><h3>TOTAL DISPONIBLE</h3><h1>${sum(saldos.values()):,}</h1></div>', unsafe_allow_html=True)
    
    # Navegación compacta
    menu = st.selectbox("Navegación:", ["📈 Estadísticas", "📊 Historial", "💸 Movimientos", "📌 Deudas", "🎯 Metas"], label_visibility="collapsed")
    
    # --- LÓGICA DE SECCIONES (Resumida para brevedad y eficiencia) ---
    if menu == "💸 Movimientos":
        # Botones de modo en 2x2 para celular
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("➕ Ingreso"): st.session_state.modo = "ing"
            if st.button("🎯 Ahorro"): st.session_state.modo = "meta"
        with c2:
            if st.button("➖ Gasto"): st.session_state.modo = "gas"
            if st.button("🔄 Transf"): st.session_state.modo = "trans"
        
        # (Aquí continúa tu lógica de formularios manteniendo el estado 'modo')
    
    # ... (El resto de tus secciones se renderizan normalmente)

    if st.button("🚪 Salir"):
        st.session_state.usuario_logeado = None
        st.rerun()
