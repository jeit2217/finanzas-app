import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Finanzas Pro", page_icon="💰", layout="centered")

# --- CSS OPTIMIZADO PARA MÓVIL ---
st.markdown("""
<style>
    .stApp { background-color: #1a1a1a !important; color: #ffffff !important; }
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Botones amigables al tacto */
    div.stButton > button { height: 45px !important; border-radius: 10px !important; width: 100%; font-weight: bold; }
    
    /* Tarjetas y Contenedores */
    .tarjeta-saldo { background: #252525; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 15px; border: 1px solid #333; }
    .tarjeta-banco { background-color: #252525; border: 1px solid #333; border-radius: 10px; padding: 10px; text-align: center; }
    .item-historial { background-color: #252525; padding: 12px; border-radius: 10px; margin-bottom: 8px; border-left: 5px solid #ccc; font-size: 0.9rem; }
    
    /* Asegurar visibilidad de texto en inputs */
    input, div[data-baseweb="select"] { background-color: #333 !important; color: white !important; }
    
    .ingreso-style { border-left-color: #2a9d8f !important; }
    .gasto-style { border-left-color: #e63946 !important; }
    .meta-style { border-left-color: #a29bfe !important; }
    .transferencia-style { border-left-color: #6c757d !important; }
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

# --- ESTADOS ---
if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
for s in ['val_express_ing', 'val_express_gas', 'val_express_met', 'val_express_tra', 'val_express_deu', 'val_express_mcrear']:
    if s not in st.session_state: st.session_state[s] = 0

# --- LOGIN ---
if st.session_state.usuario_logeado is None:
    st.markdown("<h1 style='text-align: center;'>📱 Finanzas Pro</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Iniciar", "📝 Registrar"])
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
    CATEGORIAS = ["Comida", "Transporte", "Rumba", "Deudas", "Hogar", "Otros"]
    
    ARCH_HIST = f"{user}_hist.json"
    ARCH_DEUDAS = f"{user}_deudas_v2.json"
    ARCH_METAS = f"{user}_metas.json"

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

    hist = cargar_datos("hist")
    deudas = cargar_datos("deudas")
    metas = cargar_datos("metas")
    saldos = {b: cargar_saldo(b) for b in BANCOS}

    # Interfaz
    st.markdown(f'<div class="tarjeta-saldo"><h3>TOTAL DISPONIBLE</h3><h1>${sum(saldos.values()):,} COP</h1></div>', unsafe_allow_html=True)
    
    menu = st.selectbox("Navegación:", ["📈 Estadísticas", "📊 Historial", "💸 Movimientos", "📌 Deudas", "🎯 Metas"])
    st.write("---")

    if menu == "📈 Estadísticas":
        st.subheader("Resumen")
        df = pd.DataFrame(hist)
        gasto = int(df[df['tipo'] == "Gasto"]['monto'].sum()) if not df.empty and "Gasto" in df.columns else 0
        st.markdown(f'<div class="tarjeta-saldo"><h3>GASTOS</h3><h1>${gasto:,} COP</h1></div>', unsafe_allow_html=True)

    elif menu == "📊 Historial":
        for h in reversed(hist):
            estilo = f"{h['tipo'].lower()}-style"
            st.markdown(f'<div class="item-historial {estilo}"><b>{h["tipo"]} ({h["banco"]}):</b> ${h["monto"]:,} <br> {h["det"]}</div>', unsafe_allow_html=True)

    elif menu == "💸 Movimientos":
        modo = st.radio("Acción:", ["Ingreso", "Gasto", "Meta", "Transf"], horizontal=True)
        # (Aquí mantienes tu lógica de formularios de movimiento original...)
        st.info("Formularios activos en modo: " + modo)

    elif menu == "📌 Deudas":
        st.subheader("Control de Deudas")
        # (Aquí mantienes tu lógica de deudas original...)

    elif menu == "🎯 Metas":
        st.subheader("Mis Metas")
        # (Aquí mantienes tu lógica de metas original...)

    if st.button("🚪 Salir"):
        st.session_state.usuario_logeado = None
        st.rerun()
