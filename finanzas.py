import streamlit as st
import os
import json
import pandas as pd  # Para manejar los datos del gráfico

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Finanzas Pro Stats", page_icon="📈", layout="centered")

# --- DISEÑO ---
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)
st.markdown("<style>.stApp { background-color: #121212 !important; color: #e0e0e0 !important; }</style>", unsafe_allow_html=True)

# Estilo de tarjetas (Total General)
st.markdown("<style>.tarjeta-saldo { background: linear-gradient(135deg, #1f4068 0%, #162447 100%); color: white !important; padding: 25px; border-radius: 16px; box-shadow: 0px 10px 25px rgba(0,0,0,0.15); text-align: center; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-saldo h3 {margin: 0 !important; font-size: 0.90rem !important; letter-spacing: 1.5px; opacity: 0.85; color: #f1faee !important;} .tarjeta-saldo h1 {margin: 8px 0 0 0 !important; font-size: 2.4rem !important; font-weight: 700 !important; color: #ffffff !important;}</style>", unsafe_allow_html=True)

# Cuadrícula de Bancos Individuales (¡Recuperada!)
st.markdown("<style>.contenedor-bancos {display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 25px;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco {background-color: #1b1b1b; border: 1px solid #333; border-radius: 12px; padding: 12px; text-align: center; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco p {margin: 0 !important; font-size: 0.75rem; opacity: 0.7; text-transform: uppercase; font-weight: bold; letter-spacing: 0.5px;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco h4 {margin: 5px 0 0 0 !important; font-size: 1.0rem; font-weight: 700; color: #457b9d !important;}</style>", unsafe_allow_html=True)

# Historial e ítems
st.markdown("<style>.item-historial { background-color: #1b1b1b; padding: 12px; border-radius: 10px; margin-bottom: 8px; border-left: 5px solid #444; font-size: 0.9rem;}</style>", unsafe_allow_html=True)

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
    st.title("📱 Finanzas Pro")
    t1, t2 = st.tabs(["Ingresar", "Registrarse"])
    with t1:
        u_l = st.text_input("Usuario:").lower().strip()
        p_l = st.text_input("Clave:", type="password")
        if st.button("Entrar", use_container_width=True):
            users = cargar_usuarios()
            if u_l in users and users[u_l] == p_l:
                st.session_state.usuario_logeado = u_l
                st.rerun()
    with t2:
        u_r = st.text_input("Nuevo Usuario:").lower().strip()
        p_r = st.text_input("Nueva Clave:", type="password")
        if st.button("Crear"):
            with open(ARCHIVO_USUARIOS, "a") as f: f.write(f"{u_r},{p_r}\n")
            st.success("¡Listo!")

# --- APP PRINCIPAL ---
else:
    user = st.session_state.usuario_logeado
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu"]
    CATEGORIAS = ["Comida", "Transporte", "Rumba", "Deudas", "Hogar", "Otros"]
    
    # Archivos
    ARCH_HIST = f"{user}_hist.json"
    ARCH_DEUDAS = f"{user}_deudas.json"

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

    # Cargar Info inicial
    hist = cargar_datos("hist")
    deudas = cargar_datos("deudas")
    saldos = {b: cargar_saldo(b) for b in BANCOS}
    total = sum(saldos.values())

    # --- PANTALLA VISUAL DE SALDO TOTAL ---
    st.markdown(f'<div class="tarjeta-saldo"><h3>TOTAL GENERAL DISPONIBLE</h3><h1>${total:,} COP</h1></div>', unsafe_allow_html=True)
    
    # --- CUADRÍCULA DE BANCOS INDIVIDUALES (RESTAURADA) ---
    cols_html = "".join([f'<div class="tarjeta-banco"><p>{b}</p><h4>${saldos[b]:,}</h4></div>' for b in BANCOS])
    st.markdown(f'<div class="contenedor-bancos">{cols_html}</div>', unsafe_allow_html=True)

    if st.button("🚪 Salir de la Cuenta"):
        st.session_state.usuario_logeado = None
        st.rerun()

    # PESTAÑAS PRINCIPALES
    p_stats, p_mov, p_deu = st.tabs(["📈 Estadísticas", "💸 Movimientos", "📌 Deudas"])

    # --- PESTAÑA ESTADÍSTICAS ---
    with p_stats:
        st.subheader("Análisis de Gastos")
        df = pd.DataFrame(hist)
        
        if not df.empty and "Gasto" in df['tipo'].values:
            # Filtrar solo gastos
            gastos_df = df[df['tipo'] == "Gasto"]
            
            # Agrupar por categoría
            resumen = gastos_df.groupby('cat')['monto'].sum()
            
            st.write("Distribución de consumos:")
            
            # Columnas invisibles para encoger el gráfico y centrarlo bonito
            col_izq, col_centro, col_der = st.columns([1, 4, 1])
            with col_centro:
                # Gráfico nativo en formato compacto
                st.bar_chart(resumen, height=220, use_container_width=True)
            
            st.write("---")
            # Tabla estilizada de porcentajes
            total_gastos = resumen.sum()
            for cat, monto in resumen.items():
                porcentaje = (monto / total_gastos) * 100
                st.write(f"🔹 **{cat}:** ${int(monto):,} ({porcentaje:.1f}%)")
        else:
            st.info("Aún no hay gastos registrados para analizar.")

    # --- PESTAÑA MOVIMIENTOS ---
    with p_mov:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ Ingreso", use_container_width=True): st.session_state.modo = "ing"
        with c2:
            if st.button("➖ Gasto", use_container_width=True): st.session_state.modo = "gas"

        modo = st.session_state.get('modo', 'ing')
        
        if modo == "ing":
            st.markdown("### Registrar Ingreso")
            b_i = st.selectbox("¿A dónde entra la plata?", BANCOS)
            m_i = st.number_input("Monto en COP:", min_value=0, step=1000)
            d_i = st.text_input("Detalle (Opcional):")
            if st.button("Guardar Ingreso 📈", use_container_width=True):
                if m_i > 0:
                    saldos[b_i] += m_i
                    guardar_saldo(b_i, saldos[b_i])
                    hist.append({"tipo": "Ingreso", "banco": b_i, "monto": m_i, "cat": "Ingreso", "det": d_i if d_i else "Ingreso general"})
                    guardar_datos("hist", hist)
                    st.rerun()
        else:
            st.markdown("### Registrar Gasto")
            b_g = st.selectbox("¿De dónde sale la plata?", BANCOS)
            cat_g = st.selectbox("Categoría del Gasto:", CATEGORIAS)
            m_g = st.number_input("Monto en COP:", min_value=0, step=1000)
            paga_d = st.checkbox("¿Este gasto descuenta una deuda?")
            id_d = st.text_input("ID de la Deuda:").upper().strip() if paga_d else ""
            
            if st.button("Confirmar Gasto 📉", use_container_width=True):
                if m_g > 0:
                    if m_g <= saldos[b_g]:
                        if paga_d:
                            if id_d in deudas:
                                deudas[id_d]['monto'] -= m_g
                                if deudas[id_d]['monto'] <= 0: del deudas[id_d]
                                guardar_datos("deudas", deudas)
                            else:
                                st.error("ID de deuda no válido.")
                                st.stop()
                        
                        saldos[b_g] -= m_g
                        guardar_saldo(b_g, saldos[b_g])
                        hist.append({"tipo": "Gasto", "banco": b_g, "monto": m_g, "cat": cat_g, "det": f"Abono Deuda {id_d}" if paga_d else "Gasto"})
                        guardar_datos("hist", hist)
                        st.rerun()
                    else: st.error("Fondos insuficientes en esta cuenta.")

    # --- PESTAÑA DEUDAS ---
    with p_deu:
        st.subheader("Gestión de Deudas")
        id_n = st.text_input("ID Deuda Único (Ej: JUAN):").upper().strip()
        m_n = st.number_input("Monto de la Deuda:", min_value=0, step=1000)
        if st.button("Crear Deuda 📌", use_container_width=True):
            if id_n and m_n > 0:
                deudas[id_n] = {"nombre": id_n, "monto": m_n}
                guardar_datos("deudas", deudas)
                st.rerun()
        
        st.write("---")
        for k, v in deudas.items():
            st.markdown(f'<div class="item-historial" style="border-left: 5px solid #e63946"><b>🆔 ID: {k}</b> <br> Saldo pendiente: ${v["monto"]:,} COP</div>', unsafe_allow_html=True)
