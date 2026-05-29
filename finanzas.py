import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Finanzas Pro Stats", page_icon="💰", layout="centered")

# --- DISEÑO ---
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)
st.markdown("<style>.stApp { background-color: #121212 !important; color: #e0e0e0 !important; }</style>", unsafe_allow_html=True)

# Estilo de tarjetas (Disponibles)
st.markdown("<style>.tarjeta-saldo { background: linear-gradient(135deg, #1f4068 0%, #162447 100%); color: white !important; padding: 25px; border-radius: 16px; box-shadow: 0px 10px 25px rgba(0,0,0,0.15); text-align: center; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-saldo h3 {margin: 0 !important; font-size: 0.90rem !important; letter-spacing: 1.5px; opacity: 0.85; color: #f1faee !important;} .tarjeta-saldo h1 {margin: 8px 0 0 0 !important; font-size: 2.4rem !important; font-weight: 700 !important; color: #ffffff !important;}</style>", unsafe_allow_html=True)

# Tarjeta de Gastos Totales
st.markdown("<style>.tarjeta-gastos { background: linear-gradient(135deg, #781d1d 0%, #4a0e0e 100%); color: white !important; padding: 20px; border-radius: 16px; box-shadow: 0px 10px 25px rgba(0,0,0,0.15); text-align: center; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-gastos h3 {margin: 0 !important; font-size: 0.90rem !important; letter-spacing: 1.5px; opacity: 0.85; color: #f1faee !important;} .tarjeta-gastos h1 {margin: 8px 0 0 0 !important; font-size: 2.2rem !important; font-weight: 700 !important; color: #ffffff !important;}</style>", unsafe_allow_html=True)

# Cuadrícula de Bancos Individuales
st.markdown("<style>.contenedor-bancos {display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 25px;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco {background-color: #1b1b1b; border: 1px solid #333; border-radius: 12px; padding: 12px; text-align: center; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco p {margin: 0 !important; font-size: 0.75rem; opacity: 0.7; text-transform: uppercase; font-weight: bold; letter-spacing: 0.5px;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco h4 {margin: 5px 0 0 0 !important; font-size: 1.0rem; font-weight: 700; color: #457b9d !important;}</style>", unsafe_allow_html=True)

# Historial e ítems estilizados
st.markdown("<style>.item-historial { background-color: #1b1b1b; padding: 14px 18px; border-radius: 10px; margin-bottom: 10px; border-left: 6px solid #ccc; font-family: monospace; font-size: 0.95rem; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.ingreso-style { border-left-color: #2a9d8f !important; } .gasto-style { border-left-color: #e63946 !important; } .deuda-style { border-left-color: #f4a261 !important; } .pagada-style { border-left-color: #457b9d !important; }</style>", unsafe_allow_html=True)

# --- BASE DE DATOS ---
ARCHIVO_USUARIOS = "usuarios_db.txt"

def cargar_usuarios():
    u = {}
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, "r") as f:
            for l in f:
                p = l.strip().split(",")
                if len(p) == 2: u[p[0]] = p[1]
    return u

if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None

# --- LOGIN ---
if st.session_state.usuario_logeado is None:
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>📱 Finanzas Pro</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
    with t1:
        u_l = st.text_input("Usuario:").lower().strip()
        p_l = st.text_input("Clave:", type="password")
        if st.button("Entrar 🚀", use_container_width=True):
            users = cargar_usuarios()
            if u_l in users and users[u_l] == p_l:
                st.session_state.usuario_logeado = u_l
                st.rerun()
            else: st.error("Datos incorrectos.")
    with t2:
        u_r = st.text_input("Nuevo Usuario:").lower().strip()
        p_r = st.text_input("Nueva Clave:", type="password")
        if st.button("Crear Cuenta ✨", use_container_width=True):
            if u_r and p_r:
                with open(ARCHIVO_USUARIOS, "a") as f: f.write(f"{u_r},{p_r}\n")
                st.success("¡Cuenta creada con éxito!")

# --- APP PRINCIPAL ---
else:
    user = st.session_state.usuario_logeado
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu"]
    CATEGORIAS = ["Comida", "Transporte", "Rumba", "Deudas", "Hogar", "Otros"]
    
    # Archivos
    ARCH_HIST = f"{user}_hist.json"
    ARCH_DEUDAS = f"{user}_deudas_v2.json" # Nueva estructura para soportar el historial interno

    def cargar_datos(tipo):
        p = f"{user}_{tipo}.json"
        if os.path.exists(p):
            with open(p, "r") as f: return json.load(f)
        return [] if tipo == "hist" else {}

    def guardar_datos(tipo, d):
        with open(f"{user}_{tipo}.json", "w") as f: json.dump(d, f)

    def cargar_saldo(b):
        p = f"{user}_s_{b.lower()}.txt"
        if os.path.exists(p):
            with open(p, "r") as f: return int(f.read())
        return 0

    def guardar_saldo(b, s):
        with open(f"{user}_s_{b.lower()}.txt", "w") as f: f.write(str(s))

    # Cargar información inicial
    hist = cargar_datos("hist")
    deudas = cargar_datos("deudas")
    saldos = {b: cargar_saldo(b) for b in BANCOS}
    total_disponible = sum(saldos.values())

    # --- PANTALLA VISUAL DE SALDO DISPONIBLE ---
    st.markdown(f'<div class="tarjeta-saldo"><h3>TOTAL GENERAL DISPONIBLE</h3><h1>${total_disponible:,} COP</h1></div>', unsafe_allow_html=True)
    
    # --- CUADRÍCULA DE BANCOS INDIVIDUALES ---
    cols_html = "".join([f'<div class="tarjeta-banco"><p>{b}</p><h4>${saldos[b]:,}</h4></div>' for b in BANCOS])
    st.markdown(f'<div class="contenedor-bancos">{cols_html}</div>', unsafe_allow_html=True)

    if st.button("🚪 Salir de la Cuenta", use_container_width=True):
        st.session_state.usuario_logeado = None
        st.rerun()

    # PESTAÑAS PRINCIPALES
    p_stats, p_historial, p_mov, p_deu = st.tabs(["📈 Estadísticas", "📊 Historial Completo", "💸 Registrar Movimientos", "📌 Deudas"])

    # --- PESTAÑA 1: ESTADÍSTICAS ---
    with p_stats:
        st.subheader("Resumen Analítico")
        df = pd.DataFrame(hist)
        
        total_gastado = 0
        if not df.empty and "Gasto" in df['tipo'].values:
            total_gastado = int(df[df['tipo'] == "Gasto"]['monto'].sum())
            
        st.markdown(f'<div class="tarjeta-gastos"><h3>GASTOS TOTALES ACUMULADOS</h3><h1>${total_gastado:,} COP</h1></div>', unsafe_allow_html=True)
        
        if total_gastado > 0:
            gastos_df = df[df['tipo'] == "Gasto"]
            resumen = gastos_df.groupby('cat')['monto'].sum()
            st.markdown("### Porcentaje por Categoría")
            for cat, monto in resumen.items():
                porcentaje = (monto / total_gastado) * 100
                st.write(f"🔹 **{cat}:** ${int(monto):,} ({porcentaje:.1f}%)")
        else:
            st.info("No registras gastos todavía.")

    # --- PESTAÑA 2: HISTORIAL COMPLETO INDIVIDUAL ---
    with p_historial:
        st.subheader("Lista de Movimientos Realizados")
        if len(hist) == 0:
            st.info("No hay transacciones registradas en esta cuenta.")
        else:
            for h in reversed(hist):
                if h['tipo'] == "Ingreso":
                    st.markdown(f'<div class="item-historial ingreso-style">📈 <b>Ingreso ({h["banco"]}):</b> +${h["monto"]:,} COP <br> 📝 {h["det"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="item-historial gasto-style">📉 <b>Gasto ({h["banco"]}):</b> -${h["monto"]:,} COP <br> 📁 Categoría: {h["cat"]} | {h["det"]}</div>', unsafe_allow_html=True)
            
            st.write("---")
            if st.button("🗑️ Borrar Todo el Historial", use_container_width=True, key="btn_borrar_absoluto"):
                for b in BANCOS:
                    p_b = f"{user}_s_{b.lower()}.txt"
                    if os.path.exists(p_b): os.remove(p_b)
                if os.path.exists(ARCH_HIST): os.remove(ARCH_HIST)
                if os.path.exists(ARCH_DEUDAS): os.remove(ARCH_DEUDAS)
                st.success("🗑️ ¡Historial, deudas y saldos borrados por completo!")
                st.rerun()

    # --- PESTAÑA 3: MOVIMIENTOS ---
    with p_mov:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ Registrar Ingreso", use_container_width=True): st.session_state.modo = "ing"
        with c2:
            if st.button("➖ Registrar Gasto", use_container_width=True): st.session_state.modo = "gas"

        modo = st.session_state.get('modo', 'ing')
        
        if modo == "ing":
            st.markdown("### 📈 Añadir Fondos")
            b_i = st.selectbox("¿A qué cuenta ingresa?", BANCOS)
            m_i = st.number_input("Monto en COP:", min_value=0, step=1000, key="m_i_val")
            d_i = st.text_input("Detalle o concepto:", placeholder="Ej: Sueldo, Venta", key="d_i_val")
            if st.button("Guardar Ingreso 📈", use_container_width=True):
                if m_i > 0:
                    saldos[b_i] += m_i
                    guardar_saldo(b_i, saldos[b_i])
                    hist.append({"tipo": "Ingreso", "banco": b_i, "monto": m_
