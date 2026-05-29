import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Finanzas Pro Stats", page_icon="💰", layout="centered")

# --- DISEÑO HÍBRIDO INTELIGENTE (PC / MÓVIL) ---
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)
st.markdown("<style>.stApp { background-color: #121212 !important; color: #e0e0e0 !important; }</style>", unsafe_allow_html=True)

st.markdown("""
<style>
    /* --- CONFIGURACIÓN --- */
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px !important; }
    .stTabs [data-baseweb="tab"] { padding: 12px 16px !important; font-size: 1rem !important; }
    .stButton button { min-height: 40px !important; border-radius: 10px !important; }
    .contenedor-bancos { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 20px; }
    
    /* Alertas */
    .factura-vencida { background-color: #781d1d !important; border-left: 6px solid #e63946 !important; border-radius: 8px; padding: 10px; margin-bottom: 8px; }
    .factura-alerta { background-color: #644d14 !important; border-left: 6px solid #ffb703 !important; border-radius: 8px; padding: 10px; margin-bottom: 8px; }
    .factura-al-dia { background-color: #1b1b1b !important; border-left: 6px solid #2a9d8f !important; border-radius: 8px; padding: 10px; margin-bottom: 8px; }

    /* Estilos Cajones */
    .cajon-meta { background-color: #1b1b1b; border: 1px solid #2d2d2d; border-radius: 12px; padding: 15px; margin-bottom: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
    .cajon-meta h4 { margin: 0 0 8px 0 !important; color: #a29bfe !important; font-size: 1.1rem; font-weight: bold; }
    .cajon-prestamo { background-color: #102a43; border: 1px solid #1982c4; border-radius: 12px; padding: 15px; margin-bottom: 15px; text-align: center; }
    .alerta-psicologica { background-color: #3b2314 !important; border-left: 6px solid #f39c12 !important; border-radius: 8px; padding: 12px; margin-top: 10px; margin-bottom: 15px; font-size: 0.9rem; }

    @media (max-width: 768px) {
        .contenedor-bancos { grid-template-columns: repeat(2, 1fr) !important; gap: 6px !important; }
    }
</style>
""", unsafe_allow_html=True)

# CSS Tarjetas visuales
st.markdown("<style>.tarjeta-saldo { background: linear-gradient(135deg, #1f4068 0%, #162447 100%); color: white !important; padding: 18px; border-radius: 14px; text-align: center; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-gastos { background: linear-gradient(135deg, #781d1d 0%, #4a0e0e 100%); color: white !important; padding: 18px; border-radius: 14px; text-align: center; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco {background-color: #1b1b1b; border: 1px solid #2d2d2d; border-radius: 10px; padding: 10px; text-align: center;}</style>", unsafe_allow_html=True)
st.markdown("<style>.item-historial { background-color: #1b1b1b; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid #ccc; font-family: monospace; font-size: 0.85rem;}</style>", unsafe_allow_html=True)
st.markdown("<style>.ingreso-style { border-left-color: #2a9d8f !important; } .gasto-style { border-left-color: #e63946 !important; } .meta-style { border-left-color: #a29bfe !important; } .transferencia-style { border-left-color: #6c757d !important; } .prestamo-style { border-left-color: #1982c4 !important; }</style>", unsafe_allow_html=True)

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

def procesar_monto_texto(texto):
    if not texto: return 0
    limpio = str(texto).replace(".", "").replace(",", "").replace("$", "").strip()
    if limpio.isdigit(): return int(limpio)
    return 0

# --- INICIALIZACIÓN ---
if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None

# --- LOGIN ---
if st.session_state.usuario_logeado is None:
    st.markdown("<h1 style='text-align: center;'>📱 Finanzas Pro</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Login", "📝 Registro"])
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
else:
    user = st.session_state.usuario_logeado
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu", "Guardado / Ahorro"]
    CATEGORIAS = ["Comida", "Transporte", "Rumba", "Deudas", "Hogar", "Otros"]
    
    ARCH_HIST = f"{user}_hist.json"
    ARCH_FACTURAS = f"{user}_facturas.json"
    ARCH_METAS = f"{user}_metas.json"
    ARCH_LIMITES = f"{user}_limites.json"
    ARCH_PRESTAMOS = f"{user}_prestamos.json"
    ARCH_TRABAJO = f"{user}_trabajo.json"

    def cargar_datos(tipo):
        if tipo == "hist": p = ARCH_HIST
        elif tipo == "facturas": p = ARCH_FACTURAS
        elif tipo == "limites": p = ARCH_LIMITES
        elif tipo == "prestamos": p = ARCH_PRESTAMOS
        elif tipo == "trabajo": p = ARCH_TRABAJO
        else: p = ARCH_METAS
        if os.path.exists(p):
            with open(p, "r") as f: return json.load(f)
        return [] if tipo == "hist" else {}

    def guardar_datos(tipo, d):
        if tipo == "hist": p = ARCH_HIST
        elif tipo == "facturas": p = ARCH_FACTURAS
        elif tipo == "limites": p = ARCH_LIMITES
        elif tipo == "prestamos": p = ARCH_PRESTAMOS
        elif tipo == "trabajo": p = ARCH_TRABAJO
        else: p = ARCH_METAS
        with open(p, "w") as f: json.dump(d, f)

    def cargar_saldo(b):
        nombre_arch = b.lower().replace(" / ", "_").replace(" ", "_")
        p = f"{user}_s_{nombre_arch}.txt"
        if os.path.exists(p):
            with open(p, "r") as f: return int(f.read())
        return 0

    def guardar_saldo(b, s):
        nombre_arch = b.lower().replace(" / ", "_").replace(" ", "_")
        with open(f"{user}_s_{nombre_arch}.txt", "w") as f: f.write(str(s))

    # Carga de datos
    hist = cargar_datos("hist")
    facturas = cargar_datos("facturas")
    metas = cargar_datos("metas")
    limites = cargar_datos("limites")
    prestamos = cargar_datos("prestamos")
    config_trabajo = cargar_datos("trabajo")
    saldos = {b: cargar_saldo(b) for b in BANCOS}
    total_disponible = sum(saldos.values())

    # Funciones de formato
    TASA_USD, TASA_EUR = 4100.0, 4400.0
    def formatear_moneda(valor_cop):
        return f"${valor_cop:,} COP" # Simplificado para el ejemplo, expandible

    # --- PANTALLA PRINCIPAL ---
    st.markdown(f'<div class="tarjeta-saldo"><h3>DISPONIBLE</h3><h1>{formatear_moneda(total_disponible)}</h1></div>', unsafe_allow_html=True)
    
    # --- FECHAS Y FILTRO ---
    MESES_DICT = {"01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril", "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto", "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"}
    hoy = datetime.now()
    mes_actual_num = hoy.strftime("%m")
    año_actual_num = hoy.strftime("%Y")
    mes_defecto_label = f"{MESES_DICT[mes_actual_num]} {año_actual_num}"
    
    opciones_meses = sorted({f"{MESES_DICT[datetime.strptime(h.get('fecha', '2026-01-01'), '%Y-%m-%d').strftime('%m')]} {datetime.strptime(h.get('fecha', '2026-01-01'), '%Y-%m-%d').strftime('%Y')}" for h in hist} | {mes_defecto_label}, reverse=True)
    mes_seleccionado = st.selectbox("Selecciona Periodo:", opciones_meses)
    
    hist_filtrado = [h for h in hist if f"{MESES_DICT[datetime.strptime(h.get('fecha', f'{año_actual_num}-{mes_actual_num}-01'), '%Y-%m-%d').strftime('%m')]} {datetime.strptime(h.get('fecha', f'{año_actual_num}-{mes_actual_num}-01'), '%Y-%m-%d').strftime('%Y')}" == mes_seleccionado]

    # --- TABS ---
    tab_est, tab_hist, tab_mov, tab_fac, tab_met, tab_lim, tab_pre = st.tabs(["📈 Stats", "📊 Hist", "💸 Movs", "🧾 Recibos", "🎯 Alcancías", "📉 Topes", "🤝 Préstamos"])

    with tab_est:
        st.write(f"### Resumen de {mes_seleccionado}")
        df = pd.DataFrame(hist_filtrado)
        total_gastado = int(df[df['tipo'] == "Gasto"]['monto'].sum()) if not df.empty and "Gasto" in df['tipo'].values else 0
        st.markdown(f'<div class="tarjeta-gastos"><h3>GASTADO</h3><h1>{formatear_moneda(total_gastado)}</h1></div>', unsafe_allow_html=True)
        
        resumen_gastos = {c: int(df[df['cat'] == c]['monto'].sum()) if not df.empty and "Gasto" in df['tipo'].values else 0 for c in CATEGORIAS}
        
        # --- DISEÑO RESPONSIVO INTEGRADO ---
        for cat in CATEGORIAS:
            monto_g = resumen_gastos[cat]
            tope_g = limites.get(cat, 0)
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**{cat}**")
            with col2:
                st.markdown(f"<div style='text-align: right;'>{formatear_moneda(monto_g)}</div>", unsafe_allow_html=True)
            if tope_g > 0:
                porcentaje_uso = monto_g / tope_g
                st.progress(min(porcentaje_uso, 1.0))
                if porcentaje_uso >= 1.0: st.error(f"🚨 AGOTADO: {cat}")
                elif porcentaje_uso >= 0.80: st.warning(f"⚠️ {cat}: {porcentaje_uso*100:.0f}%")
            st.divider()

    with tab_hist:
        for h in reversed(hist_filtrado):
            st.markdown(f'<div class="item-historial"><b>{h["tipo"]} | {h["monto"]}</b> <br> {h["det"]}</div>', unsafe_allow_html=True)

    with tab_mov:
        modo = st.radio("Acción:", ["Ingreso", "Gasto", "Ahorro", "Transferencia"], horizontal=True)
        # (Nota: Aquí iría la lógica de formularios de entrada simplificada)
        st.write("Módulo de movimientos activos...")

    with tab_fac:
        st.write("### Control de Recibos")
        # (Aquí va la lógica de facturas)

    with tab_met:
        st.write("### Alcancías")
        # (Aquí va la lógica de metas)

    with tab_lim:
        st.write("### Topes Mensuales")
        # (Aquí va la lógica de límites)

    with tab_pre:
        st.write("### Préstamos")
        # (Aquí va la lógica de préstamos)

    if st.button("🚪 Cerrar Sesión"):
        st.session_state.usuario_logeado = None
        st.rerun()
