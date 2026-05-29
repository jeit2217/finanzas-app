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
    /* --- CONFIGURACIÓN PARA PC / ESCRITORIO --- */
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px !important; }
    .stTabs [data-baseweb="tab"] { padding: 12px 16px !important; font-size: 1rem !important; }
    .stButton button { min-height: 40px !important; border-radius: 10px !important; }
    .contenedor-bancos { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 20px; }

    /* Estilos para las alertas de facturas */
    .factura-vencida { background-color: #781d1d !important; border-left: 6px solid #e63946 !important; border-radius: 8px; padding: 10px; margin-bottom: 8px; }
    .factura-alerta { background-color: #644d14 !important; border-left: 6px solid #ffb703 !important; border-radius: 8px; padding: 10px; margin-bottom: 8px; }
    .factura-al-dia { background-color: #1b1b1b !important; border-left: 6px solid #2a9d8f !important; border-radius: 8px; padding: 10px; margin-bottom: 8px; }

    /* Estilos para los CAJONES DE METAS */
    .cajon-meta {
        background-color: #1b1b1b;
        border: 1px solid #2d2d2d;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .cajon-meta h4 { margin: 0 0 8px 0 !important; color: #a29bfe !important; font-size: 1.1rem; font-weight: bold; }
    .cajon-meta p { margin: 2px 0 !important; font-size: 0.85rem; opacity: 0.9; }
    .cajon-meta .porcentaje { font-size: 1.2rem; font-weight: bold; color: #2a9d8f; margin: 5px 0 !important; }

    /* Estilos para los CAJONES DE PRÉSTAMOS (AZULES) */
    .cajon-prestamo {
        background-color: #102a43;
        border: 1px solid #1982c4;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .cajon-prestamo h4 { margin: 0 0 5px 0 !important; color: #9bccf8 !important; font-size: 1.1rem; font-weight: bold; }
    .cajon-prestamo p { margin: 2px 0 !important; font-size: 0.85rem; opacity: 0.9; }
    .cajon-prestamo .monto-deuda { font-size: 1.25rem; font-weight: bold; color: #ffadad; margin: 5px 0 !important; }

    /* Alerta psicológica del convertidor de trabajo quincenal */
    .alerta-psicologica {
        background-color: #3b2314 !important;
        border-left: 6px solid #f39c12 !important;
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
        margin-bottom: 15px;
        font-size: 0.9rem;
    }

    /* --- REGLAS ESPECÍFICAS PARA CELULARES --- */
    @media (max-width: 768px) {
        .block-container { 
            padding-top: 0.6rem !important; 
            padding-bottom: 0.6rem !important; 
            padding-left: 0.5rem !important; 
            padding-right: 0.5rem !important; 
        }
        .stTabs [data-baseweb="tab-list"] { gap: 2px !important; width: 100% !important; }
        .stTabs [data-baseweb="tab"] { 
            padding: 8px 2px !important; 
            font-size: 0.68rem !important; 
            flex-grow: 1 !important; 
            text-align: center !important; 
        }
        .stButton button { min-height: 44px !important; border-radius: 12px !important; font-size: 0.88rem !important; }
        
        [data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 6px !important;
        }
        [data-testid="stHorizontalBlock"] > div:last-child {
            grid-column: span 3 !important;
        }
        .contenedor-bancos { grid-template-columns: repeat(2, 1fr) !important; gap: 6px !important; }
    }
</style>
""", unsafe_allow_html=True)

# Tarjetas visuales fijas
st.markdown("<style>.tarjeta-saldo { background: linear-gradient(135deg, #1f4068 0%, #162447 100%); color: white !important; padding: 18px; border-radius: 14px; text-align: center; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-saldo h3 {margin: 0 !important; font-size: 0.8rem !important; letter-spacing: 1px; opacity: 0.8; color: #f1faee !important;} .tarjeta-saldo h1 {margin: 4px 0 0 0 !important; font-size: 2rem !important; font-weight: 700 !important; color: #ffffff !important;}</style>", unsafe_allow_html=True)

st.markdown("<style>.tarjeta-gastos { background: linear-gradient(135deg, #781d1d 0%, #4a0e0e 100%); color: white !important; padding: 18px; border-radius: 14px; text-align: center; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-gastos h3 {margin: 0 !important; font-size: 0.8rem !important; letter-spacing: 1px; opacity: 0.8; color: #f1faee !important;} .tarjeta-gastos h1 {margin: 4px 0 0 0 !important; font-size: 1.8rem !important; font-weight: 700 !important; color: #ffffff !important;}</style>", unsafe_allow_html=True)

st.markdown("<style>.tarjeta-banco {background-color: #1b1b1b; border: 1px solid #2d2d2d; border-radius: 10px; padding: 10px; text-align: center;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco p {margin: 0 !important; font-size: 0.7rem; opacity: 0.6; text-transform: uppercase; font-weight: bold;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco h4 {margin: 2px 0 0 0 !important; font-size: 1rem; font-weight: 700; color: #457b9d !important;}</style>", unsafe_allow_html=True)

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

# --- INICIALIZACIÓN DE VARIABLES EXPRÉS ---
if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
if 'val_express_ing' not in st.session_state: st.session_state.val_express_ing = 0
if 'val_express_gas' not in st.session_state: st.session_state.val_express_gas = 0
if 'val_express_met' not in st.session_state: st.session_state.val_express_met = 0
if 'val_express_tra' not in st.session_state: st.session_state.val_express_tra = 0
if 'val_express_deu' not in st.session_state: st.session_state.val_express_deu = 0
if 'val_express_mcrear' not in st.session_state: st.session_state.val_express_mcrear = 0

# --- LOGIN ---
if st.session_state.usuario_logeado is None:
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-weight: 800; font-size: 1.8rem;'>📱 Finanzas Pro</h1>", unsafe_allow_html=True)
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

# --- APP PRINCIPAL ---
else:
    user = st.session_state.usuario_logeado
    # AGREGADA LA OPCIÓN DE "GUARDADO / AHORRO"
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
        # Reemplazar caracteres especiales para nombres de archivos limpios
        nombre_arch = b.lower().replace(" / ", "_").replace(" ", "_")
        p = f"{user}_s_{nombre_arch}.txt"
        if os.path.exists(p):
            with open(p, "r") as f: return int(f.read())
        return 0

    def guardar_saldo(b, s):
        nombre_arch = b.lower().replace(" / ", "_").replace(" ", "_")
        with open(f"{user}_s_{nombre_arch}.txt", "w") as f: f.write(str(s))

    hist = cargar_datos("hist")
    facturas = cargar_datos("facturas")
    metas = cargar_datos("metas")
    limites = cargar_datos("limites")
    prestamos = cargar_datos("prestamos")
    config_trabajo = cargar_datos("trabajo")
    saldos = {b: cargar_saldo(b) for b in BANCOS}
    total_disponible = sum(saldos.values())

    # --- LÓGICA DE CONVERSIÓN A MONEDA ESTABLE ---
    st.write("### 💱 Visualización de Divisa")
    moneda_visual = st.radio("Ver saldos y estadísticas en:", ["COP 🇨🇴", "USD 🇺🇸", "EUR 🇪🇺"], horizontal=True)
    
    # Tasas de cambio promedio
    TASA_USD = 4100.0
    TASA_EUR = 4400.0
    
    def formatear_moneda(valor_cop):
        if moneda_visual == "USD 🇺🇸":
            return f"${valor_cop / TASA_USD:,.2f} USD"
        elif moneda_visual == "EUR 🇪🇺":
            return f"€{valor_cop / TASA_EUR:,.2f} EUR"
        else:
            return f"${valor_cop:,} COP"

    # --- PANTALLA FIJA SUPERIOR CON DIVISA ---
    st.markdown(f'<div class="tarjeta-saldo"><h3>DISPONIBLE GENERAL</h3><h1>{formatear_moneda(total_disponible)}</h1></div>', unsafe_allow_html=True)
    cols_html = "".join([f'<div class="tarjeta-banco"><p>{b}</p><h4>{formatear_moneda(saldos[b])}</h4></div>' for b in BANCOS])
    st.markdown(f'<div class="contenedor-bancos">{cols_html}</div>', unsafe_allow_html=True)

    # --- MÓDULO DE FECHAS ---
    MESES_DICT = {"01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril", "05": "Mayo", "06": "Junio", 
                  "07": "Julio", "08": "Agosto", "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"}
    hoy = datetime.now()
    mes_actual_num = hoy.strftime("%m")
    año_actual_num = hoy.strftime("%Y")
    mes_defecto_label = f"{MESES_DICT[mes_actual_num]} {año_actual_num}"

    opciones_meses = set()
    for h in hist:
        if "fecha" not in h: h["fecha"] = f"{año_actual_num}-{mes_actual_num}-01"
        fecha_obj = datetime.strptime(h["fecha"], "%Y-%m-%d")
        lbl = f"{MESES_DICT[fecha_obj.strftime('%m')]} {fecha_obj.strftime('%Y')}"
        opciones_meses.add(lbl)
    
    opciones_meses.add(mes_defecto_label)
    lista_meses_ordenada = sorted(list(opciones_meses), reverse=True)

    st.write("### 📅 Filtro de Periodo")
    mes_seleccionado = st.selectbox("Selecciona el mes a revisar:", lista_meses_ordenada)

    hist_filtrado = []
    for h in hist:
        fecha_obj = datetime.strptime(h.get("fecha", f"{año_actual_num}-{mes_actual_num}-01"), "%Y-%m-%d")
        lbl = f"{MESES_DICT[fecha_obj.strftime('%m')]} {fecha_obj.strftime('%Y')}"
        if lbl == mes_seleccionado: hist_filtrado.append(h)

    # --- NAVEGACIÓN EN TABS ---
    tab_est, tab_hist, tab_mov, tab_fac, tab_met, tab_lim, tab_pre = st.tabs(["📈 Stats", "📊 Hist", "💸 Movs", "🧾 Recibos", "🎯 Alcancías", "📉 Topes", "🤝 Préstamos"])

    # --- SECCIÓN 1: ESTADÍSTICAS ---
    with tab_est:
        st.write(f"### Resumen de {mes_seleccionado}")
        df = pd.DataFrame(hist_filtrado)
        total_gastado = 0
        if not df.empty and "Gasto" in df['tipo'].values:
            total_gastado = int(df[df['tipo'] == "Gasto"]['monto'].sum())
        
        st.markdown(f'<div class="tarjeta-gastos"><h3>GASTADO EN ESTE MES</h3><h1>{formatear_moneda(total_gastado)}</h1></div>', unsafe_allow_html=True)
        
        st.write("#### 🔍 Gastos por Categoría:")
        resumen_gastos = {c: 0 for c in CATEGORIAS}
        if not df.empty and "Gasto" in df['tipo'].values:
            gastos_df = df[df['tipo'] == "Gasto"]
            for c in CATEGORIAS: resumen_gastos[c] = int(gastos_df[gastos_df['cat'] == c]['monto'].sum())

        for cat in CATEGORIAS:
            monto_g = resumen_gastos[cat]
            tope_g = limites.get(cat, 0)
            col_a, col_b = st.columns([3, 1])
            with col_a: 
                texto_limite = f" / {formatear_moneda(tope_g)}" if tope_g > 0 else ""
                st.write(f"🔹 **{cat}:** {formatear_moneda(monto_g)}{texto_limite}")
            with col_b:
                if total_gastado > 0 and monto_g > 0: st.write(f"({(monto_g/total_gastado)*100:.0f}%)")
            if tope_g > 0:
                porcentaje_uso = monto_g / tope_g
                st.progress(min(porcentaje_uso, 1.0))
                if porcentaje_uso >= 1.0: st.error(f"🚨 ¡AGOTADO! Superaste el límite de {cat} por {formatear_moneda(monto_g - tope_g)}!")
                elif porcentaje_uso >= 0.80: st.warning(f"⚠️ ¡Cuidado! Has gastado el {porcentaje_uso*100:.0f}% de tu cupo en {cat}.")
            st.write("")

    # --- SECCIÓN 2: HISTORIAL ---
    with tab_hist:
        st.write(f"### Transacciones de {mes_seleccionado}")
        if len(hist_filtrado) == 0: st.info("No hay movimientos en este periodo.")
        else:
            for h in reversed(hist_filtrado):
                f_formateada = h.get("fecha", "")
                monto_formateado = formatear_moneda(h["monto"])
                if h['tipo'] == "Ingreso":
                    st.markdown(f'<div class="item-historial ingreso-style">📈 <b>[{f_formateada}] Ingreso ({h["banco"]}):</b> +{monto_formateado} <br> 📝 {h["det"]}</div>', unsafe_allow_html=True)
                elif h['tipo'] == "Meta":
                    st.markdown(f'<div class="item-historial meta-style">🎯 <b>[{f_formateada}] Ahorro Meta ({h["banco"]}):</b> -{monto_formateado} <br> 🚀 Para: {h["det"]}</div>', unsafe_allow_html=True)
                elif h['tipo'] == "Transferencia":
                    st.markdown(f'<div class="item-historial transferencia-style">🔄 <b>[{f_formateada}] Transferencia:</b> {monto_formateado} <br> 🏦 Desde {h["banco"]} hacia {h["cat"]}</div>', unsafe_allow_html=True)
                elif h['tipo'] == "Prestamo":
                    st.markdown(f'<div class="item-historial prestamo-style">🤝 <b>[{f_formateada}] Dinero Prestado ({h["banco"]}):</b> -{monto_formateado} <br> 👤 A favor de: {h["det"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="item-historial gasto-style">📉 <b>[{f_formateada}] Gasto ({h["banco"]}):</b> -{monto_formateado} <br> 📁 {h["cat"]} | {h["det"]}</div>', unsafe_allow_html=True)

    # --- SECCIÓN 3: MOVIMIENTOS ---
    with tab_mov:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("➕ Ingreso", key="btn_m_ing", use_container_width=True): st.session_state.modo = "ing"
        with c2:
            if st.button("➖ Gasto", key="btn_m_gas", use_container_width=True): st.session_state.modo = "gas"
        with c3:
            if st.button("🎯 Ahorro", key="btn_m_met", use_container_width=True): st.session_state.modo = "meta"
        with c4:
            if st.button("🔄 Transf.", key="btn_m_tra", use_container_width=True): st.session_state.modo = "trans"
        
        modo_actual = st.session_state.get('modo', 'ing')
        hoy_str = hoy.strftime("%Y-%m-%d")
        st.write("---")
        
        if modo_actual == "ing":
            st.write("### 📈 Añadir Fondos")
            with st.form("form_ingreso", clear_on_submit=True):
                b_i = st.selectbox("¿Cuenta de destino?", BANCOS)
                txt_m_i = st.text_input("Monto en COP:")
                d_i = st.text_input("Detalle:")
                if st.form_submit_button("Guardar Ingreso 📈", use_container_width=True):
                    m_i = procesar_monto_texto(txt_m_i)
                    if m_i > 0:
                        saldos[b_i] += m_i; guardar_saldo(b_i, saldos[b_i])
                        hist.append({"tipo": "Ingreso", "banco": b_i, "monto": m_i, "cat": "Ingreso", "det": d_i if d_i else "Ingreso general", "fecha": hoy_str})
                        guardar_datos("hist", hist); st.rerun()
        
        elif modo_actual == "gas":
            st.write("### 📉 Registrar Gasto")
            txt_m_g = st.text_input("Monto en COP:", key="monto_gasto_realtime")
            m_g_temp = procesar_monto_texto(txt_m_g)
            
            # --- ALERTA PSICOLÓGICA QUINCENAL ---
            if config_trabajo and m_g_temp > 0:
                sueldo_quincenal = config_trabajo.get("sueldo", 0)
                horas_quincenales = config_trabajo.get("horas", 80)
                if sueldo_quincenal > 0 and horas_quincenales > 0:
                    valor_hora = sueldo_quincenal / horas_quincenales
                    horas_necesarias = m_g_temp / valor_hora
                    
                    if horas_necesarias >= horas_quincenales:
                        quincenas = horas_necesarias / horas_quincenales
                        msg_psico = f"⏳ Alerta: Este gasto equivale a **{quincenas:.1f} quincenas** de tu salario de trabajo."
                    elif horas_necesarias >= 8:
                        dias = horas_necesarias / 8
                        msg_psico = f"⏳ Alerta: Este gasto equivale a **{dias:.1f} días** completos de tu jornada laboral."
                    else:
                        msg_psico = f"⏳ Alerta: Este gasto equivale a **{horas_necesarias:.1f} horas** de tu tiempo de trabajo."
                    
                    st.markdown(f'<div class="alerta-psicologica">🛒 {msg_psico}<br><span style="font-size:0.75rem; opacity:0.8;">¿Realmente vale la pena cambiar ese esfuerzo de tu quincena por este artículo? 🤔</span></div>', unsafe_allow_html=True)

            with st.form("form_gasto", clear_on_submit=True):
                b_g = st.selectbox("¿De dónde sale el dinero?", BANCOS)
                cat_g = st.selectbox("Categoría:", CATEGORIAS)
                det_g = st.text_input("Detalle del gasto:")
                
                if st.form_submit_button("Confirmar Gasto 📉", use_container_width=True):
                    if m_g_temp > 0 and m_g_temp <= saldos[b_g]:
                        saldos[b_g] -= m_g_temp; guardar_saldo(b_g, saldos[b_g])
                        hist.append({"tipo": "Gasto", "banco": b_g, "monto": m_g_temp, "cat": cat_g, "det": det_g if det_g else f"Gasto en {cat_g}", "fecha": hoy_str})
                        guardar_datos("hist", hist); st.rerun()
                    elif m_g_temp > saldos[b_g]:
                        st.error("❌ No tienes fondos suficientes en esa cuenta.")

        elif modo_actual == "meta":
            if not metas: st.warning("Crea una meta primero.")
            else:
                st.write("### 🎯 Guardar para una Meta")
                with st.form("form_meta", clear_on_submit=True):
                    b_m = st.selectbox("¿Cuenta origen?", BANCOS)
                    meta_dest = st.selectbox("¿Para cuál objetivo?", list(metas.keys()))
                    txt_m_m = st.text_input("Monto a ahorrar:")
                    if st.form_submit_button("Confirmar Ahorro 🚀", use_container_width=True):
                        m_m = procesar_monto_texto(txt_m_m)
                        if m_m > 0 and m_m <= saldos[b_m]:
                            saldos[b_m] -= m_m; guardar_saldo(b_m, saldos[b_m])
                            metas[meta_dest]['ahorrado'] += m_m
                            guardar_datos("metas", metas)
                            hist.append({"tipo": "Meta", "banco": b_m, "monto": m_m, "cat": "Ahorro", "det": meta_dest, "fecha": hoy_str})
                            guardar_datos("hist", hist); st.rerun()

        elif modo_actual == "trans":
            st.write("### 🔄 Transferir Dinero")
            with st.form("form_transferencia", clear_on_submit=True):
                b_origen = st.selectbox("Desde cuenta:", BANCOS)
                b_destino = st.selectbox("Hacia cuenta:", BANCOS)
                txt_m_t = st.text_input("Monto:")
                if st.form_submit_button("Confirmar 🔄", use_container_width=True):
                    m_t = procesar_monto_texto(txt_m_t)
                    if b_origen != b_destino and m_t > 0 and m_t <= saldos[b_origen]:
                        saldos[b_origen] -= m_t; saldos[b_destino] += m_t
                        guardar_saldo(b_origen, saldos[b_origen]); guardar_saldo(b_destino, saldos[b_destino])
                        hist.append({"tipo": "Transferencia", "banco": b_origen, "monto": m_t, "cat": b_destino, "det": f"A {b_destino}", "fecha": hoy_str})
                        guardar_datos("hist", hist); st.rerun()

    # --- SECCIÓN 4: RECIBOS ---
    with tab_fac:
        st.write("### 🧾 Control de Recibos")
        with st.form("form_crear_factura", clear_on_submit=True):
            nombre_f = st.text_input("Nombre del Servicio:")
            cat_f = st.selectbox("Categoría:", CATEGORIAS, index=4) 
            txt_m_f = st.text_input("Costo mensual:")
            fecha_vencimiento_inicial = st.date_input("Próximo vencimiento:", value=hoy)
            if st.form_submit_button("Registrar 🧾", use_container_width=True):
                m_f = procesar_monto_texto(txt_m_f)
                if nombre_f and m_f > 0:
                    facturas[nombre_f] = {"monto": m_f, "fecha_vencimiento": fecha_vencimiento_inicial.strftime("%Y-%m-%d"), "cat": cat_f, "ultimo_pago": "Nunca"}
                    guardar_datos("facturas", facturas); st.rerun()

        if facturas:
            for name, data in list(facturas.items()):
                fecha_vence_obj = datetime.strptime(data["fecha_vencimiento"], "%Y-%m-%d")
                monto_fac = data["monto"]
                dias_restantes = (fecha_vence_obj.date() - hoy.date()).days
                clase_css = "factura-vencida" if dias_restantes < 0 else ("factura-alerta" if dias_restantes <= 5 else "factura-al-dia")
                
                st.markdown(f'<div class="{clase_css}"><h4>{name}</h4><p>{formatear_moneda(monto_fac)} | Vence: {fecha_vence_obj.strftime("%d/%m")}</p><p style="font-size:0.7rem;">Último: {data.get("ultimo_pago", "Nunca")}</p></div>', unsafe_allow_html=True)
                banco_pago = st.selectbox("Pagar con:", BANCOS, key=f"b_{name}")
                if st.button("PAGAR NOW 💸", key=f"p_{name}"):
                    if saldos[banco_pago] >= monto_fac:
                        saldos[banco_pago] -= monto_fac; guardar_saldo(banco_pago, saldos[banco_pago])
                        hist.append({"tipo": "Gasto", "banco": banco_pago, "monto": monto_fac, "cat": data["cat"], "det": f"Factura: {name}", "fecha": hoy_str})
                        guardar_datos("hist", hist)
                        data["ultimo_pago"] = hoy.strftime("%d/%m/%Y")
                        data["fecha_vencimiento"] = (fecha_vence_obj + timedelta(days=30)).strftime("%Y-%m-%d")
                        guardar_datos("facturas", facturas); st.rerun()

    # --- SECCIÓN 5: METAS ---
    with tab_met:
        st.write("### 🎯 Mis Alcancías de Ahorro")
        with st.expander("➕ Crear Nueva Alcancía / Meta"):
            with st.form("form_crear_meta", clear_on_submit=True):
                nombre_m = st.text_input("¿Qué deseas lograr? (Ej: Viaje, Celular)").strip()
                txt_total_m = st.text_input("Precio total estimado (COP):")
                if st.form_submit_button("Establecer Objetivo 🎯", use_container_width=True):
                    total_m = procesar_monto_texto(txt_total_m)
                    if nombre_m and total_m > 0:
                        metas[nombre_m] = {"objetivo": total_m, "ahorrado": 0}
                        guardar_datos("metas", metas); st.rerun()

        st.write("---")
        if not metas: st.info("No tienes alcancías creadas.")
        else:
            items_metas = list(metas.items())
            for i in range(0, len(items_metas), 3):
                bloque = items_metas[i:i+3]
                columnas = st.columns(3)
                for idx, (m_nombre, m_datos) in enumerate(bloque):
                    with columnas[idx]:
                        objetivo = m_datos['objetivo']
                        ahorrado = m_datos['ahorrado']
                        porcentaje = (ahorrado / objetivo) * 100 if objetivo > 0 else 0
                        porcentaje = min(porcentaje, 100.0)
                        
                        st.markdown(f'<div class="cajon-meta"><h4>📦 {m_nombre}</h4><p class="porcentaje">{porcentaje:.0f}%</p><p><b>Ahorrado:</b><br>{formatear_moneda(ahorrado)}</p><p style="opacity: 0.6; font-size: 0.75rem;">Meta: {formatear_moneda(objetivo)}</p></div>', unsafe_allow_html=True)
                        st.progress(porcentaje / 100)
                        if st.button("🗑️ Romper", key=f"del_{m_nombre}", use_container_width=True):
                            del metas[m_nombre]; guardar_datos("metas", metas); st.rerun()
                st.write("")

    # --- SECCIÓN 6: CONFIGURACIÓN DE TOPES + CONFIG TRABAJO QUINCENAL ---
    with tab_lim:
        st.write("### 📉 Configurar Límites Mensuales")
        with st.form("form_limites"):
            cat_limite = st.selectbox("Categoría a limitar:", CATEGORIAS)
            monto_limite_txt = st.text_input("Presupuesto mensual (COP):")
            if st.form_submit_button("Guardar Límite 💾", use_container_width=True):
                m_lim = procesar_monto_texto(monto_limite_txt)
                if m_lim >= 0:
                    limites[cat_limite] = m_lim
                    guardar_datos("limites", limites); st.rerun()
        
        if limites:
            for c, m in list(limites.items()):
                if m > 0:
                    if st.button(f"Eliminar Límite {c}: {formatear_moneda(m)}", key=f"del_lim_{c}", use_container_width=True):
                        del limites[c]; guardar_datos("limites", limites); st.rerun()
                        
        st.write("---")
        st.write("### ⏳ Configuración de Psicología del Gasto (Quincenal)")
        st.write("Introduce tus ingresos y tiempos medidos por quincena:")
        
        sueldo_actual_conf = config_trabajo.get("sueldo", 0)
        horas_actual_conf = config_trabajo.get("horas", 80)
        
        with st.form("form_psico_trabajo"):
            txt_sueldo = st.text_input("¿Cuánto recibes neto en cada QUINCENA (COP)?", value=f"{sueldo_actual_conf:,}" if sueldo_actual_conf else "")
            horas_lab = st.number_input("¿Cuántas horas laboras por QUINCENA?", min_value=1, max_value=200, value=horas_actual_conf)
            
            if st.form_submit_button("Guardar Configuración Quincenal 💾", use_container_width=True):
                sueldo_num = procesar_monto_texto(txt_sueldo)
                if sueldo_num > 0 and horas_lab > 0:
                    config_trabajo = {"sueldo": sueldo_num, "horas": horas_lab}
                    guardar_datos("trabajo", config_trabajo)
                    st.success("¡Configuración quincenal de tiempo guardada!")
                    st.rerun()
                    
        if config_trabajo:
            v_hora = config_trabajo['sueldo'] / config_trabajo['horas']
            st.info(f"💡 Tu hora de trabajo equivale actualmente a: **{formatear_moneda(int(v_hora))}** basado en tu quincena.")

    # --- SECCIÓN 7: 🤝 HISTORIAL DE DINERO PRESTADO ---
    with tab_pre:
        st.write("### 🤝 Control de Dinero Prestado")
        with st.expander("💸 Registrar Nuevo Préstamo"):
            with st.form("form_crear_prestamo", clear_on_submit=True):
                persona_p = st.text_input("¿A quién le prestaste? (Nombre):").strip()
                banco_p = st.selectbox("¿De qué cuenta salió el dinero?", BANCOS)
                txt_monto_p = st.text_input("Monto prestado (COP):")
                if st.form_submit_button("Confirmar Préstamo 💸", use_container_width=True):
                    monto_p = procesar_monto_texto(txt_monto_p)
                    if persona_p and monto_p > 0 and monto_p <= saldos[banco_p]:
                        saldos[banco_p] -= monto_p; guardar_saldo(banco_p, saldos[banco_p])
                        id_prestamo = f"{persona_p}_{datetime.now().strftime('%M%S')}"
                        prestamos[id_prestamo] = {"persona": persona_p, "monto": monto_p, "banco_origen": banco_p, "fecha": hoy.strftime("%d/%m/%Y")}
                        guardar_datos("prestamos", prestamos)
                        hist.append({"tipo": "Prestamo", "banco": banco_p, "monto": monto_p, "cat": "Deudas", "det": persona_p, "fecha": hoy.strftime("%Y-%m-%d")})
                        guardar_datos("hist", hist); st.rerun()
                    elif monto_p > saldos[banco_p]: st.error("❌ No tienes fondos suficientes.")

        st.write("---")
        if not prestamos: st.info("¡Al día! Nadie te debe dinero actualmente. 😎")
        else:
            items_prestamos = list(prestamos.items())
            for i in range(0, len(items_prestamos), 3):
                bloque_p = items_prestamos[i:i+3]
                columnas_p = st.columns(3)
                for idx, (p_id, p_datos) in enumerate(bloque_p):
                    with columnas_p[idx]:
                        st.markdown(f'<div class="cajon-prestamo"><h4>👤 {p_datos["persona"]}</h4><p class="monto-deuda">-{formatear_moneda(p_datos["monto"])}</p><p style="font-size: 0.75rem; opacity: 0.8;">Salió de: {p_datos["banco_origen"]}</p><p style="font-size: 0.7rem; opacity: 0.5;">Prestado: {p_datos["fecha"]}</p></div>', unsafe_allow_html=True)
                        banco_retorno = st.selectbox("¿Dónde te pagó?", BANCOS, key=f"ret_{p_id}")
                        if st.button("¡Ya me pagó! ✅", key=f"pay_{p_id}", use_container_width=True):
                            saldos[banco_retorno] += p_datos['monto']; guardar_saldo(banco_retorno, saldos[banco_retorno])
                            hist.append({"tipo": "Ingreso", "banco": banco_retorno, "monto": p_datos['monto'], "cat": "Ingreso", "det": f"Pago recibido de {p_datos['persona']}", "fecha": hoy.strftime("%Y-%m-%d")})
                            guardar_datos("hist", hist)
                            del prestamos[p_id]; guardar_datos("prestamos", prestamos); st.rerun()
                st.write("")

    # --- BOTÓN DE SALIDA ---
    st.write("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.usuario_logeado = None
        st.rerun()
