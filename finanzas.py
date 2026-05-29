import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime

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
    .contenedor-bancos { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }

    /* Estilos para las alertas de facturas */
    .factura-vencida { background-color: #781d1d !important; border-left: 6px solid #e63946 !important; border-radius: 8px; padding: 10px; margin-bottom: 8px; }
    .factura-alerta { background-color: #644d14 !important; border-left: 6px solid #ffb703 !important; border-radius: 8px; padding: 10px; margin-bottom: 8px; }
    .factura-al-dia { background-color: #1b1b1b !important; border-left: 6px solid #2a9d8f !important; border-radius: 8px; padding: 10px; margin-bottom: 8px; }

    /* --- REGLAS ESPECÍFICAS PARA CELULARES (Pantallas menores a 768px) --- */
    @media (max-width: 768px) {
        .block-container { 
            padding-top: 0.6rem !important; 
            padding-bottom: 0.6rem !important; 
            padding-left: 0.5rem !important; 
            padding-right: 0.5rem !important; 
        }
        .stTabs [data-baseweb="tab-list"] { gap: 2px !important; width: 100% !important; }
        .stTabs [data-baseweb="tab"] { 
            padding: 8px 4px !important; 
            font-size: 0.75rem !important; 
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

# Tarjetas visuales
st.markdown("<style>.tarjeta-saldo { background: linear-gradient(135deg, #1f4068 0%, #162447 100%); color: white !important; padding: 18px; border-radius: 14px; text-align: center; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-saldo h3 {margin: 0 !important; font-size: 0.8rem !important; letter-spacing: 1px; opacity: 0.8; color: #f1faee !important;} .tarjeta-saldo h1 {margin: 4px 0 0 0 !important; font-size: 2rem !important; font-weight: 700 !important; color: #ffffff !important;}</style>", unsafe_allow_html=True)

st.markdown("<style>.tarjeta-gastos { background: linear-gradient(135deg, #781d1d 0%, #4a0e0e 100%); color: white !important; padding: 18px; border-radius: 14px; text-align: center; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-gastos h3 {margin: 0 !important; font-size: 0.8rem !important; letter-spacing: 1px; opacity: 0.8; color: #f1faee !important;} .tarjeta-gastos h1 {margin: 4px 0 0 0 !important; font-size: 1.8rem !important; font-weight: 700 !important; color: #ffffff !important;}</style>", unsafe_allow_html=True)

st.markdown("<style>.tarjeta-banco {background-color: #1b1b1b; border: 1px solid #2d2d2d; border-radius: 10px; padding: 10px; text-align: center;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco p {margin: 0 !important; font-size: 0.7rem; opacity: 0.6; text-transform: uppercase; font-weight: bold;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco h4 {margin: 2px 0 0 0 !important; font-size: 1rem; font-weight: 700; color: #457b9d !important;}</style>", unsafe_allow_html=True)

st.markdown("<style>.item-historial { background-color: #1b1b1b; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid #ccc; font-family: monospace; font-size: 0.85rem;}</style>", unsafe_allow_html=True)
st.markdown("<style>.ingreso-style { border-left-color: #2a9d8f !important; } .gasto-style { border-left-color: #e63946 !important; } .deuda-style { border-left-color: #f4a261 !important; } .meta-style { border-left-color: #a29bfe !important; } .transferencia-style { border-left-color: #6c757d !important; }</style>", unsafe_allow_html=True)

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
    limpio = texto.replace(".", "").replace(",", "").replace("$", "").strip()
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
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu"]
    CATEGORIAS = ["Comida", "Transporte", "Rumba", "Deudas", "Hogar", "Otros"]
    
    ARCH_HIST = f"{user}_hist.json"
    ARCH_FACTURAS = f"{user}_facturas.json"  # Reemplaza el antiguo de deudas
    ARCH_METAS = f"{user}_metas.json"
    ARCH_LIMITES = f"{user}_limites.json"

    def cargar_datos(tipo):
        if tipo == "hist": p = ARCH_HIST
        elif tipo == "facturas": p = ARCH_FACTURAS
        elif tipo == "limites": p = ARCH_LIMITES
        else: p = ARCH_METAS
        
        if os.path.exists(p):
            with open(p, "r") as f: return json.load(f)
        return [] if tipo == "hist" else {}

    def guardar_datos(tipo, d):
        if tipo == "hist": p = ARCH_HIST
        elif tipo == "facturas": p = ARCH_FACTURAS
        elif tipo == "limites": p = ARCH_LIMITES
        else: p = ARCH_METAS
        with open(p, "w") as f: json.dump(d, f)

    def cargar_saldo(b):
        p = f"{user}_s_{b.lower()}.txt"
        if os.path.exists(p):
            with open(p, "r") as f: return int(f.read())
        return 0

    def guardar_saldo(b, s):
        with open(f"{user}_s_{b.lower()}.txt", "w") as f: f.write(str(s))

    hist = cargar_datos("hist")
    facturas = cargar_datos("facturas")
    metas = cargar_datos("metas")
    limites = cargar_datos("limites")
    saldos = {b: cargar_saldo(b) for b in BANCOS}
    total_disponible = sum(saldos.values())

    # --- PANTALLA FIJA SUPERIOR ---
    st.markdown(f'<div class="tarjeta-saldo"><h3>DISPONIBLE GENERAL</h3><h1>${total_disponible:,} COP</h1></div>', unsafe_allow_html=True)
    cols_html = "".join([f'<div class="tarjeta-banco"><p>{b}</p><h4>${saldos[b]:,}</h4></div>' for b in BANCOS])
    st.markdown(f'<div class="contenedor-bancos">{cols_html}</div>', unsafe_allow_html=True)

    # --- MÓDULO DE TRATAMIENTO DE FECHAS ---
    MESES_DICT = {"01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril", "05": "Mayo", "06": "Junio", 
                  "07": "Julio", "08": "Agosto", "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"}
    hoy = datetime.now()
    mes_actual_num = hoy.strftime("%m")
    año_actual_num = hoy.strftime("%Y")
    dia_actual = hoy.day
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
    tab_est, tab_hist, tab_mov, tab_fac, tab_met, tab_lim = st.tabs(["📈 Stats", "📊 Hist", "💸 Movs", "🧾 Recibos", "🎯 Metas", "📉 Topes"])

    # --- SECCIÓN 1: ESTADÍSTICAS ---
    with tab_est:
        st.write(f"### Resumen de {mes_seleccionado}")
        df = pd.DataFrame(hist_filtrado)
        total_gastado = 0
        if not df.empty and "Gasto" in df['tipo'].values:
            total_gastado = int(df[df['tipo'] == "Gasto"]['monto'].sum())
        
        st.markdown(f'<div class="tarjeta-gastos"><h3>GASTADO EN ESTE MES</h3><h1>${total_gastado:,} COP</h1></div>', unsafe_allow_html=True)
        
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
                if ...: st.write(f"🔹 **{cat}:** ${monto_g:,}" + (f" / ${tope_g:,}" if tope_g > 0 else ""))
            with col_b:
                if total_gastado > 0 and monto_g > 0: st.write(f"({(monto_g/total_gastado)*100:.0f}%)")
            
            if tope_g > 0:
                porcentaje_uso = monto_g / tope_g
                st.progress(min(porcentaje_uso, 1.0))
                if porcentaje_uso >= 1.0: st.error(f"🚨 ¡AGOTADO! Superaste el límite de {cat} por ${monto_g - tope_g:,}!")
                elif porcentaje_uso >= 0.80: st.warning(f"⚠️ ¡Cuidado! Has gastado el {porcentaje_uso*100:.0f}% de tu cupo en {cat}.")
            st.write("")

    # --- SECCIÓN 2: HISTORIAL ---
    with tab_hist:
        st.write(f"### Transacciones de {mes_seleccionado}")
        if len(hist_filtrado) == 0: st.info("No hay movimientos en este periodo.")
        else:
            for h in reversed(hist_filtrado):
                f_formateada = h.get("fecha", "")
                if h['tipo'] == "Ingreso":
                    st.markdown(f'<div class="item-historial ingreso-style">📈 <b>[{f_formateada}] Ingreso ({h["banco"]}):</b> +${h["monto"]:,} <br> 📝 {h["det"]}</div>', unsafe_allow_html=True)
                elif h['tipo'] == "Meta":
                    st.markdown(f'<div class="item-historial meta-style">🎯 <b>[{f_formateada}] Ahorro Meta ({h["banco"]}):</b> -${h["monto"]:,} <br> 🚀 Para: {h["det"]}</div>', unsafe_allow_html=True)
                elif h['tipo'] == "Transferencia":
                    st.markdown(f'<div class="item-historial transferencia-style">🔄 <b>[{f_formateada}] Transferencia:</b> ${h["monto"]:,} <br> 🏦 Desde {h["banco"]} hacia {h["cat"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="item-historial gasto-style">📉 <b>[{f_formateada}] Gasto ({h["banco"]}):</b> -${h["monto"]:,} <br> 📁 {h["cat"]} | {h["det"]}</div>', unsafe_allow_html=True)
            st.write("---")
            if st.button("🗑️ Resetear Todo de Raíz", use_container_width=True):
                for b in BANCOS:
                    if os.path.exists(f"{user}_s_{b.lower()}.txt"): os.remove(f"{user}_s_{b.lower()}.txt")
                if os.path.exists(ARCH_HIST): os.remove(ARCH_HIST)
                if os.path.exists(ARCH_METAS): os.remove(ARCH_METAS)
                if os.path.exists(ARCH_LIMITES): os.remove(ARCH_LIMITES)
                if os.path.exists(ARCH_FACTURAS): os.remove(ARCH_FACTURAS)
                st.rerun()

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
        hoy_str = datetime.now().strftime("%Y-%m-%d")
        st.write("---")
        
        if modo_actual == "ing":
            st.write("### 📈 Añadir Fondos")
            b1, b2, b3, b4, b5, b6, b_clr = st.columns(7)
            with b1:
                if st.button("+2k", key="i_2k"): st.session_state.val_express_ing += 2000
            with b2:
                if st.button("+5k", key="i_5k"): st.session_state.val_express_ing += 5000
            with b3:
                if st.button("+10k", key="i_10k"): st.session_state.val_express_ing += 10000
            with b4:
                if st.button("+20k", key="i_20k"): st.session_state.val_express_ing += 20000
            with b5:
                if st.button("+50k", key="i_50k"): st.session_state.val_express_ing += 50000
            with b6:
                if st.button("+100k", key="i_100k"): st.session_state.val_express_ing += 100000
            with b_clr:
                if st.button("🧹 Limpiar Valor", key="i_clr"): st.session_state.val_express_ing = 0

            with st.form("form_ingreso", clear_on_submit=True):
                b_i = st.selectbox("¿Cuenta de destino?", BANCOS)
                val_inicial = f"{st.session_state.val_express_ing:,}" if st.session_state.val_express_ing > 0 else ""
                txt_m_i = st.text_input("Monto en COP:", value=val_inicial, placeholder="Monto final")
                d_i = st.text_input("Detalle:")
                if st.form_submit_button("Guardar Ingreso 📈", use_container_width=True):
                    m_i = procesar_monto_texto(txt_m_i)
                    if m_i > 0:
                        saldos[b_i] += m_i
                        guardar_saldo(b_i, saldos[b_i])
                        hist.append({"tipo": "Ingreso", "banco": b_i, "monto": m_i, "cat": "Ingreso", "det": d_i if d_i else "Ingreso general", "fecha": hoy_str})
                        guardar_datos("hist", hist)
                        st.session_state.val_express_ing = 0
                        st.rerun()
                    else: st.error("Monto inválido.")
        
        elif modo_actual == "gas":
            st.write("### 📉 Registrar Gasto")
            b1, b2, b3, b4, b5, b6, b_clr = st.columns(7)
            with b1:
                if st.button("+2k", key="g_2k"): st.session_state.val_express_gas += 2000
            with b2:
                if st.button("+5k", key="g_5k"): st.session_state.val_express_gas += 5000
            with b3:
                if st.button("+10k", key="g_10k"): st.session_state.val_express_gas += 10000
            with b4:
                if st.button("+20k", key="g_20k"): st.session_state.val_express_gas += 20000
            with b5:
                if st.button("+50k", key="g_50k"): st.session_state.val_express_gas += 50000
            with b6:
                if st.button("+100k", key="g_100k"): st.session_state.val_express_gas += 100000
            with b_clr:
                if st.button("🧹 Limpiar Valor", key="g_clr"): st.session_state.val_express_gas = 0

            with st.form("form_gasto", clear_on_submit=True):
                b_g = st.selectbox("¿De dónde sale el dinero?", BANCOS)
                cat_g = st.selectbox("Categoría:", CATEGORIAS)
                val_inicial = f"{st.session_state.val_express_gas:,}" if st.session_state.val_express_gas > 0 else ""
                txt_m_g = st.text_input("Monto en COP:", value=val_inicial, placeholder="Monto final")
                det_g = st.text_input("Detalle del gasto:")
                
                if st.form_submit_button("Confirmar Gasto 📉", use_container_width=True):
                    m_g = procesar_monto_texto(txt_m_g)
                    if m_g > 0 and m_g <= saldos[b_g]:
                        saldos[b_g] -= m_g
                        guardar_saldo(b_g, saldos[b_g])
                        hist.append({"tipo": "Gasto", "banco": b_g, "monto": m_g, "cat": cat_g, "det": det_g if det_g else f"Gasto en {cat_g}", "fecha": hoy_str})
                        guardar_datos("hist", hist)
                        st.session_state.val_express_gas = 0
                        st.rerun()
                    elif m_g > saldos[b_g]: st.error("Saldo insuficiente.")
                    else: st.error("Monto inválido.")
        
        elif modo_actual == "meta":
            if not metas: st.warning("Crea una meta primero en la pestaña 🎯 Metas.")
            else:
                st.write("### 🎯 Guardar para una Meta")
                b1, b2, b3, b4, b5, b6, b_clr = st.columns(7)
                # ... botones express ...
                with st.form("form_meta", clear_on_submit=True):
                    b_m = st.selectbox("¿Cuenta origen?", BANCOS)
                    meta_dest = st.selectbox("¿Para cuál objetivo?", list(metas.keys()))
                    txt_m_m = st.text_input("Monto a ahorrar:")
                    if st.form_submit_button("Confirmar Ahorro 🚀", use_container_width=True):
                        m_m = procesar_monto_texto(txt_m_m)
                        if m_m > 0 and m_m <= saldos[b_m]:
                            saldos[b_m] -= m_m
                            guardar_saldo(b_m, saldos[b_m])
                            metas[meta_dest]['ahorrado'] += m_m
                            guardar_datos("metas", metas)
                            hist.append({"tipo": "Meta", "banco": b_m, "monto": m_m, "cat": "Ahorro", "det": meta_dest, "fecha": hoy_str})
                            guardar_datos("hist", hist)
                            st.rerun()

        elif modo_actual == "trans":
            st.write("### 🔄 Transferir Dinero")
            with st.form("form_transferencia", clear_on_submit=True):
                b_origen = st.selectbox("Desde cuenta:", BANCOS, key="origen")
                b_destino = st.selectbox("Hacia cuenta:", BANCOS, key="destino")
                txt_m_t = st.text_input("Monto total:")
                if st.form_submit_button("Confirmar Transferencia 🔄", use_container_width=True):
                    m_t = procesar_monto_texto(txt_m_t)
                    if b_origen != b_destino and m_t > 0 and m_t <= saldos[b_origen]:
                        saldos[b_origen] -= m_t; saldos[b_destino] += m_t
                        guardar_saldo(b_origen, saldos[b_origen]); guardar_saldo(b_destino, saldos[b_destino])
                        hist.append({"tipo": "Transferencia", "banco": b_origen, "monto": m_t, "cat": b_destino, "det": f"Mover a {b_destino}", "fecha": hoy_str})
                        guardar_datos("hist", hist); st.rerun()

    # --- NUEVA SECCIÓN 4: FACTURAS Y SUSCRIPCIONES (Reemplaza Deudas) ---
    with tab_fac:
        st.write("### 🧾 Control de Facturas y Suscripciones Fijas")
        st.write("Registra tus recibos, suscripciones (Netflix, Spotify) o arriendos para ver cuándo vencen.")

        with st.form("form_crear_factura", clear_on_submit=True):
            nombre_f = st.text_input("Nombre de la Factura/Servicio:", placeholder="Ej: Internet Claro, Netflix, Arriendo")
            cat_f = st.selectbox("Categoría de Gasto:", CATEGORIAS, index=4) # Por defecto Hogar o Otros
            txt_m_f = st.text_input("Costo mensual (COP):")
            dia_pago = st.number_input("¿Qué día del mes vence?", min_value=1, max_value=31, value=10)
            
            if st.form_submit_button("Registrar Servicio 🧾", use_container_width=True):
                m_f = procesar_monto_texto(txt_m_f)
                if nombre_f and m_f > 0:
                    facturas[nombre_f] = {"monto": m_f, "dia_vencimiento": int(dia_pago), "cat": cat_f}
                    guardar_datos("facturas", facturas)
                    st.success(f"¡{nombre_f} programado con éxito!")
                    st.rerun()
                else: st.error("Completa todos los campos correctamente.")

        st.write("---")
        st.write("#### 📆 Estado de tus Pagos Mensuales")
        
        if not facturas: st.info("No tienes facturas o suscripciones guardadas.")
        else:
            # Procesar alertas en un bucle limpio tradicional
            for name, data in list(facturas.items()):
                vence = data["dia_vencimiento"]
                monto_fac = data["monto"]
                categoria_fac = data["cat"]

                # Calcular días restantes de forma inteligente
                dias_restantes = vence - dia_actual
                
                if dias_restantes < 0:
                    clase_css = "factura-vencida"
                    estado_texto = f"🚨 ¡VENCIDO! (Se pasó hace {-dias_restantes} días)"
                elif 0 <= dias_restantes <= 5:
                    clase_css = "factura-alerta"
                    estado_texto = f"⚠️ Alerta: Vence en {dias_restantes} días"
                else:
                    clase_css = "factura-al-dia"
                    estado_texto = f"✅ Al día (Vence en {dias_restantes} días)"

                # Tarjeta visual con contenedor CSS personalizado
                st.markdown(f"""
                <div class="{clase_css}">
                    <p style='margin:0; font-size:0.75rem; opacity:0.8;'>{estado_texto} | Vence el día: {vence}</p>
                    <h4 style='margin:2px 0; font-size:1.1rem;'>{name}</h4>
                    <p style='margin:0; font-size:0.9rem; font-weight:bold;'>${monto_fac:,} COP</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Acciones de pago directo por cada factura
                col_p1, col_p2 = st.columns([2, 1])
                with col_p1:
                    banco_pago = st.selectbox(f"¿Con qué pagas {name}?", BANCOS, key=f"banco_{name}")
                with col_p2:
                    if st.button("PAGAR NOW 💸", key=f"pay_{name}", use_container_width=True):
                        if saldos[banco_pago] >= monto_fac:
                            # 1. Descuenta del banco seleccionado
                            saldos[banco_pago] -= monto_fac
                            guardar_saldo(banco_pago, saldos[banco_pago])
                            # 2. Genera el gasto directo al historial del mes
                            hist.append({
                                "tipo": "Gasto", 
                                "banco": banco_pago, 
                                "monto": monto_fac, 
                                "cat": categoria_fac, 
                                "det": f"Pago Factura: {name}", 
                                "fecha": hoy_str
                            })
                            guardar_datos("hist", hist)
                            st.success(f"¡{name} pagado con éxito desde {banco_pago}!")
                            st.rerun()
                        else:
                            st.error("Saldo insuficiente en esa cuenta.")
                
                if st.button(f"🗑️ Eliminar Suscripción: {name}", key=f"del_fac_{name}", use_container_width=True):
                    del facturas[name]
                    guardar_datos("facturas", facturas)
                    st.rerun()
                st.write("---")

    # --- SECCIÓN 5: METAS ---
    with tab_met:
        st.write("### 🎯 Metas de Ahorro")
        with st.form("form_crear_meta", clear_on_submit=True):
            nombre_m = st.text_input("¿Qué deseas lograr?").strip()
            txt_total_m = st.text_input("Precio total estimado:")
            if st.form_submit_button("Establecer Meta 🎯", use_container_width=True):
                total_m = procesar_monto_texto(txt_total_m)
                if nombre_m and total_m > 0:
                    metas[nombre_m] = {"objetivo": total_m, "ahorrado": 0}
                    guardar_datos("metas", metas); st.rerun()

        if metas:
            for m_nombre, m_datos in metas.items():
                progreso = m_datos['ahorrado'] / m_datos['objetivo']
                st.write(f"**{m_nombre}** (${m_datos['ahorrado']:,} de ${m_datos['objetivo']:,})")
                st.progress(min(progreso, 1.0))
                if st.button(f"Eliminar: {m_nombre}", key=f"del_{m_nombre}", use_container_width=True):
                    del metas[m_nombre]; guardar_datos("metas", metas); st.rerun()

    # --- SECCIÓN 6: CONFIGURACIÓN DE TOPES/LÍMITES ---
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
                    if st.button(f"Eliminar Límite {c}: ${m:,} COP", key=f"del_lim_{c}", use_container_width=True):
                        del limites[c]; guardar_datos("limites", limites); st.rerun()

    # --- BOTÓN DE SALIDA ---
    st.write("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.usuario_logeado = None
        st.rerun()
