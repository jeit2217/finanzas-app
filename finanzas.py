import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Finanzas Pro Stats", page_icon="💰", layout="centered")

# --- DISEÑO HÍBRIDO INTELIGENTE (PC / MÓVIL) ---
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)
st.markdown("<style>.stApp { background-color: #121212 !important; color: #e0e0e0 !important; }</style>", unsafe_allow_html=True)

# Estilos responsivos adaptativos según el tamaño de la pantalla
st.markdown("""
<style>
    /* --- CONFIGURACIÓN PARA PC / ESCRITORIO --- */
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px !important; }
    .stTabs [data-baseweb="tab"] { padding: 12px 16px !important; font-size: 1rem !important; }
    .stButton button { min-height: 40px !important; border-radius: 10px !important; }
    .contenedor-bancos { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }

    /* --- REGLES ESPECÍFICAS PARA CELULARES (Pantallas menores a 768px) --- */
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
        
        /* Fuerza al teclado exprés a ordenarse en rejilla de 3 columnas en celular */
        [data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 6px !important;
        }
        /* El último botón (🧹 Limpiar Valor) ocupa todo el ancho inferior en celular */
        [data-testid="stHorizontalBlock"] > div:last-child {
            grid-column: span 3 !important;
        }
        .contenedor-bancos { grid-template-columns: repeat(2, 1fr) !important; gap: 6px !important; }
    }
</style>
""", unsafe_allow_html=True)

# Tarjetas visuales optimizadas
st.markdown("<style>.tarjeta-saldo { background: linear-gradient(135deg, #1f4068 0%, #162447 100%); color: white !important; padding: 18px; border-radius: 14px; text-align: center; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-saldo h3 {margin: 0 !important; font-size: 0.8rem !important; letter-spacing: 1px; opacity: 0.8; color: #f1faee !important;} .tarjeta-saldo h1 {margin: 4px 0 0 0 !important; font-size: 2rem !important; font-weight: 700 !important; color: #ffffff !important;}</style>", unsafe_allow_html=True)

st.markdown("<style>.tarjeta-gastos { background: linear-gradient(135deg, #781d1d 0%, #4a0e0e 100%); color: white !important; padding: 18px; border-radius: 14px; text-align: center; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-gastos h3 {margin: 0 !important; font-size: 0.8rem !important; letter-spacing: 1px; opacity: 0.8; color: #f1faee !important;} .tarjeta-gastos h1 {margin: 4px 0 0 0 !important; font-size: 1.8rem !important; font-weight: 700 !important; color: #ffffff !important;}</style>", unsafe_allow_html=True)

st.markdown("<style>.tarjeta-banco {background-color: #1b1b1b; border: 1px solid #2d2d2d; border-radius: 10px; padding: 10px; text-align: center;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco p {margin: 0 !important; font-size: 0.7rem; opacity: 0.6; text-transform: uppercase; font-weight: bold;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco h4 {margin: 2px 0 0 0 !important; font-size: 1rem; font-weight: 700; color: #457b9d !important;}</style>", unsafe_allow_html=True)

st.markdown("<style>.item-historial { background-color: #1b1b1b; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid #ccc; font-family: monospace; font-size: 0.85rem;}</style>", unsafe_allow_html=True)
st.markdown("<style>.ingreso-style { border-left-color: #2a9d8f !important; } .gasto-style { border-left-color: #e63946 !important; } .deuda-style { border-left-color: #f4a261 !important; } .pagada-style { border-left-color: #457b9d !important; } .meta-style { border-left-color: #a29bfe !important; } .transferencia-style { border-left-color: #6c757d !important; }</style>", unsafe_allow_html=True)

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
    if not texto:
        return 0
    limpio = texto.replace(".", "").replace(",", "").replace("$", "").strip()
    if limpio.isdigit():
        return int(limpio)
    return 0

# --- INICIALIZACIÓN DE VALORES EXPRÉS ---
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
    ARCH_DEUDAS = f"{user}_deudas_v2.json"
    ARCH_METAS = f"{user}_metas.json"

    def cargar_datos(tipo):
        if tipo == "hist": p = ARCH_HIST
        elif tipo == "deudas": p = ARCH_DEUDAS
        else: p = ARCH_METAS
        
        if os.path.exists(p):
            with open(p, "r") as f: return json.load(f)
        return [] if tipo == "hist" else {}

    def guardar_datos(tipo, d):
        if tipo == "hist": p = ARCH_HIST
        elif tipo == "deudas": p = ARCH_DEUDAS
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
    deudas = cargar_datos("deudas")
    metas = cargar_datos("metas")
    saldos = {b: cargar_saldo(b) for b in BANCOS}
    total_disponible = sum(saldos.values())

    # --- PANTALLA FIJA SUPERIOR ---
    st.markdown(f'<div class="tarjeta-saldo"><h3>DISPONIBLE GENERAL</h3><h1>${total_disponible:,} COP</h1></div>', unsafe_allow_html=True)
    cols_html = "".join([f'<div class="tarjeta-banco"><p>{b}</p><h4>${saldos[b]:,}</h4></div>' for b in BANCOS])
    st.markdown(f'<div class="contenedor-bancos">{cols_html}</div>', unsafe_allow_html=True)

    # --- NAVEGACIÓN EN TABS RESPONSIVOS ---
    tab_est, tab_hist, tab_mov, tab_deu, tab_met = st.tabs(["📈 Stats", "📊 Historial", "💸 Movimientos", "📌 Deudas", "🎯 Metas"])

    # --- SECCIÓN 1: ESTADÍSTICAS ---
    with tab_est:
        st.write("### Resumen Analítico")
        df = pd.DataFrame(hist)
        total_gastado = 0
        if not df.empty and "Gasto" in df['tipo'].values:
            total_gastado = int(df[df['tipo'] == "Gasto"]['monto'].sum())
        st.markdown(f'<div class="tarjeta-gastos"><h3>GASTOS ACUMULADOS</h3><h1>${total_gastado:,} COP</h1></div>', unsafe_allow_html=True)
        if total_gastado > 0:
            gastos_df = df[df['tipo'] == "Gasto"]
            resumen = gastos_df.groupby('cat')['monto'].sum()
            for cat, monto in resumen.items():
                porcentaje = (monto / total_gastado) * 100
                st.write(f"🔹 **{cat}:** ${int(monto):,} ({porcentaje:.0f}%)")
        else: st.info("No hay gastos registrados.")

    # --- SECCIÓN 2: HISTORIAL COMPLETO ---
    with tab_hist:
        st.write("### Lista de Transacciones")
        if len(hist) == 0: st.info("Historial vacío.")
        else:
            for h in reversed(hist):
                if h['tipo'] == "Ingreso":
                    st.markdown(f'<div class="item-historial ingreso-style">📈 <b>Ingreso ({h["banco"]}):</b> +${h["monto"]:,} <br> 📝 {h["det"]}</div>', unsafe_allow_html=True)
                elif h['tipo'] == "Meta":
                    st.markdown(f'<div class="item-historial meta-style">🎯 <b>Ahorro Meta ({h["banco"]}):</b> -${h["monto"]:,} <br> 🚀 Para: {h["det"]}</div>', unsafe_allow_html=True)
                elif h['tipo'] == "Transferencia":
                    st.markdown(f'<div class="item-historial transferencia-style">🔄 <b>Transferencia:</b> ${h["monto"]:,} <br> 🏦 Desde {h["banco"]} hacia {h["cat"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="item-historial gasto-style">📉 <b>Gasto ({h["banco"]}):</b> -${h["monto"]:,} <br> 📁 {h["cat"]} | {h["det"]}</div>', unsafe_allow_html=True)
            st.write("---")
            if st.button("🗑️ Resetear Datos y Cuentas", use_container_width=True):
                for b in BANCOS:
                    if os.path.exists(f"{user}_s_{b.lower()}.txt"): os.remove(f"{user}_s_{b.lower()}.txt")
                if os.path.exists(ARCH_HIST): os.remove(ARCH_HIST)
                if os.path.exists(ARCH_METAS): os.remove(ARCH_METAS)
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
                        hist.append({"tipo": "Ingreso", "banco": b_i, "monto": m_i, "cat": "Ingreso", "det": d_i if d_i else "Ingreso general"})
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
                paga_d = st.checkbox("¿Paga alguna deuda?")
                id_d = st.text_input("ID Deuda (Opcional):").upper().strip()
                
                if st.form_submit_button("Confirmar Gasto 📉", use_container_width=True):
                    m_g = procesar_monto_texto(txt_m_g)
                    if m_g > 0 and m_g <= saldos[b_g]:
                        if paga_d:
                            if id_d in deudas and deudas[id_d]['estado'] == "activa":
                                deudas[id_d]['monto_pendiente'] -= m_g
                                deudas[id_d]['historial_pagos'].append(f"Abono de ${m_g:,} COP desde {b_g}")
                                if deudas[id_d]['monto_pendiente'] <= 0:
                                    deudas[id_d]['monto_pendiente'] = 0
                                    deudas[id_d]['estado'] = "pagada"
                                    deudas[id_d]['historial_pagos'].append("🎉 ¡Pagada!")
                                guardar_datos("deudas", deudas)
                            else: st.error("ID de deuda inválido."); st.stop()
                        saldos[b_g] -= m_g
                        guardar_saldo(b_g, saldos[b_g])
                        hist.append({"tipo": "Gasto", "banco": b_g, "monto": m_g, "cat": cat_g, "det": f"Abono ID: {id_d}" if paga_d else f"Gasto: {cat_g}"})
                        guardar_datos("hist", hist)
                        st.session_state.val_express_gas = 0
                        st.rerun()
                    elif m_g > saldos[b_g]: st.error("Saldo insuficiente.")
                    else: st.error("Monto inválido.")
        
        elif modo_actual == "meta":
            if not metas:
                st.warning("Crea una meta primero en la pestaña 🎯 Metas.")
            else:
                st.write("### 🎯 Guardar para una Meta")
                b1, b2, b3, b4, b5, b6, b_clr = st.columns(7)
                with b1:
                    if st.button("+2k", key="m_2k"): st.session_state.val_express_met += 2000
                with b2:
                    if st.button("+5k", key="m_5k"): st.session_state.val_express_met += 5000
                with b3:
                    if st.button("+10k", key="m_10k"): st.session_state.val_express_met += 10000
                with b4:
                    if st.button("+20k", key="m_20k"): st.session_state.val_express_met += 20000
                with b5:
                    if st.button("+50k", key="m_50k"): st.session_state.val_express_met += 50000
                with b6:
                    if st.button("+100k", key="m_100k"): st.session_state.val_express_met += 100000
                with b_clr:
                    if st.button("🧹 Limpiar Valor", key="m_clr"): st.session_state.val_express_met = 0

                with st.form("form_meta", clear_on_submit=True):
                    b_m = st.selectbox("¿Cuenta origen?", BANCOS)
                    meta_dest = st.selectbox("¿Para cuál objetivo?", list(metas.keys()))
                    val_inicial = f"{st.session_state.val_express_met:,}" if st.session_state.val_express_met > 0 else ""
                    txt_m_m = st.text_input("Monto a ahorrar:", value=val_inicial, placeholder="Monto final")
                    if st.form_submit_button("Confirmar Ahorro 🚀", use_container_width=True):
                        m_m = procesar_monto_texto(txt_m_m)
                        if m_m > 0 and m_m <= saldos[b_m]:
                            saldos[b_m] -= m_m
                            guardar_saldo(b_m, saldos[b_m])
                            metas[meta_dest]['ahorrado'] += m_m
                            guardar_datos("metas", metas)
                            hist.append({"tipo": "Meta", "banco": b_m, "monto": m_m, "cat": "Ahorro", "det": meta_dest})
                            guardar_datos("hist", hist)
                            st.session_state.val_express_met = 0
                            st.rerun()
                        elif m_m > saldos[b_m]: st.error("Saldo insuficiente.")
                        else: st.error("Monto inválido.")

        elif modo_actual == "trans":
            st.write("### 🔄 Transferir Dinero")
            b1, b2, b3, b4, b5, b6, b_clr = st.columns(7)
            with b1:
                if st.button("+2k", key="t_2k"): st.session_state.val_express_tra += 2000
            with b2:
                if st.button("+5k", key="t_5k"): st.session_state.val_express_tra += 5000
            with b3:
                if st.button("+10k", key="t_10k"): st.session_state.val_express_tra += 10000
            with b4:
                if st.button("+20k", key="t_20k"): st.session_state.val_express_tra += 20000
            with b5:
                if st.button("+50k", key="t_50k"): st.session_state.val_express_tra += 50000
            with b6:
                if st.button("+100k", key="t_100k"): st.session_state.val_express_tra += 100000
            with b_clr:
                if st.button("🧹 Limpiar Valor", key="t_clr"): st.session_state.val_express_tra = 0

            with st.form("form_transferencia", clear_on_submit=True):
                b_origen = st.selectbox("Desde cuenta:", BANCOS, key="origen")
                b_destino = st.selectbox("Hacia cuenta:", BANCOS, key="destino")
                val_inicial = f"{st.session_state.val_express_tra:,}" if st.session_state.val_express_tra > 0 else ""
                txt_m_t = st.text_input("Monto total:", value=val_inicial, placeholder="Monto final")
                if st.form_submit_button("Confirmar Transferencia 🔄", use_container_width=True):
                    m_t = procesar_monto_texto(txt_m_t)
                    if b_origen == b_destino: st.error("Las cuentas deben ser diferentes.")
                    elif m_t > 0 and m_t <= saldos[b_origen]:
                        saldos[b_origen] -= m_t
                        saldos[b_destino] += m_t
                        guardar_saldo(b_origen, saldos[b_origen])
                        guardar_saldo(b_destino, saldos[b_destino])
                        hist.append({"tipo": "Transferencia", "banco": b_origen, "monto": m_t, "cat": b_destino, "det": f"Mover de {b_origen} a {b_destino}"})
                        guardar_datos("hist", hist)
                        st.session_state.val_express_tra = 0
                        st.rerun()
                    elif m_t > saldos[b_origen]: st.error("Saldo insuficiente.")
                    else: st.error("Monto inválido.")

    # --- SECCIÓN 4: DEUDAS ---
    with tab_deu:
        st.write("### 📌 Registro de Deudas")
        b1, b2, b3, b4, b5, b6, b_clr = st.columns(7)
        with b1:
            if st.button("+2k", key="d_2k"): st.session_state.val_express_deu += 2000
        with b2:
            if st.button("+5k", key="d_5k"): st.session_state.val_express_deu += 5000
        with b3:
            if st.button("+10k", key="d_10k"): st.session_state.val_express_deu += 10000
        with b4:
            if st.button("+20k", key="d_20k"): st.session_state.val_express_deu += 20000
        with b5:
            if st.button("+50k", key="d_50k"): st.session_state.val_express_deu += 50000
        with b6:
            if st.button("+100k", key="d_100k"): st.session_state.val_express_deu += 100000
        with b_clr:
            if st.button("🧹 Limpiar Valor", key="d_clr"): st.session_state.val_express_deu = 0

        with st.form("form_crear_deuda", clear_on_submit=True):
            id_n = st.text_input("ID de cobro:", placeholder="Ejem: PEDRO1").upper().strip()
            concepto_n = st.text_input("¿Qué te prestaron?")
            val_inicial = f"{st.session_state.val_express_deu:,}" if st.session_state.val_express_deu > 0 else ""
            txt_m_n = st.text_input("Saldo Inicial:", value=val_inicial, placeholder="Monto final")
            if st.form_submit_button("Crear Deuda 📌", use_container_width=True):
                m_n = procesar_monto_texto(txt_m_n)
                if id_n and m_n > 0 and concepto_n:
                    if id_n in deudas: st.error("Ese ID ya existe.")
                    else:
                        deudas[id_n] = {"concepto": concepto_n, "monto_inicial": m_n, "monto_pendiente": m_n, "estado": "activa", "historial_pagos": [f"Creada por ${m_n:,}"]}
                        guardar_datos("deudas", deudas)
                        st.session_state.val_express_deu = 0
                        st.session_state["deuda_creada_ok"] = True
                else: st.error("Completa todos los campos.")
        if st.session_state.pop("deuda_creada_ok", False): st.rerun()

        d_act = {k: v for k, v in deudas.items() if v.get('estado', 'activa') == "activa"}
        d_pag = {k: v for k, v in deudas.items() if v.get('estado', 'activa') == "pagada"}
        
        st.write("#### 📋 Cuentas Pendientes")
        for k, v in d_act.items():
            with st.expander(f"🔴 {k} | Debe: ${v['monto_pendiente']:,}"):
                st.write(f"**Concepto:** {v['concepto']}"); [st.write(f"• {p}") for p in v['historial_pagos']]
        
        st.write("#### ✅ Pagadas")
        for k, v in d_pag.items():
            with st.expander(f"🟢 {k} [Cerrada]"):
                st.write(f"**Concepto:** {v['concepto']}"); [st.write(f"• {p}") for p in v['historial_pagos']]

        st.write("---")
        if st.button("🗑️ Borrar Registro de Deudas", use_container_width=True):
            if os.path.exists(ARCH_DEUDAS): os.remove(ARCH_DEUDAS); st.rerun()

    # --- SECCIÓN 5: METAS ---
    with tab_met:
        st.write("### 🎯 Metas de Ahorro")
        b1, b2, b3, b4, b5, b6, b_clr = st.columns(7)
        with b1:
            if st.button("+2k", key="mc_2k"): st.session_state.val_express_mcrear += 2000
        with b2:
            if st.button("+5k", key="mc_5k"): st.session_state.val_express_mcrear += 5000
        with b3:
            if st.button("+10k", key="mc_10k"): st.session_state.val_express_mcrear += 10000
        with b4:
            if st.button("+20k", key="mc_20k"): st.session_state.val_express_mcrear += 20000
        with b5:
            if st.button("+50k", key="mc_50k"): st.session_state.val_express_mcrear += 50000
        with b6:
            if st.button("+100k", key="mc_100k"): st.session_state.val_express_mcrear += 100000
        with b_clr:
            if st.button("🧹 Limpiar Valor", key="mc_clr"): st.session_state.val_express_mcrear = 0

        with st.form("form_crear_meta", clear_on_submit=True):
            nombre_m = st.text_input("¿Qué deseas lograr?", placeholder="Ej: Viaje").strip()
            val_inicial = f"{st.session_state.val_express_mcrear:,}" if st.session_state.val_express_mcrear > 0 else ""
            txt_total_m = st.text_input("Precio total estimado:", value=val_inicial)
            if st.form_submit_button("Establecer Meta 🎯", use_container_width=True):
                total_m = procesar_monto_texto(txt_total_m)
                if nombre_m and total_m > 0:
                    metas[nombre_m] = {"objetivo": total_m, "ahorrado": 0}
                    guardar_datos("metas", metas)
                    st.session_state.val_express_mcrear = 0
                    st.session_state["meta_creada_ok"] = True
                else: st.error("Verifica los campos.")
        if st.session_state.pop("meta_creada_ok", False): st.rerun()

        st.write("---")
        if not metas: st.info("Sin objetivos activos.")
        else:
            for m_nombre, m_datos in metas.items():
                progreso = m_datos['ahorrado'] / m_datos['objetivo']
                progreso = min(progreso, 1.0)
                st.write(f"**{m_nombre}** (${m_datos['ahorrado']:,} de ${m_datos['objetivo']:,})")
                st.progress(progreso)
                if progreso >= 1.0: 
                    st.balloons(); st.success("¡Completado! 🥳")
                if st.button(f"Eliminar: {m_nombre}", key=f"del_{m_nombre}", use_container_width=True):
                    del metas[m_nombre]; guardar_datos("metas", metas); st.rerun()

        st.write("---")
        if st.button("🗑️ Resetear Metas Completas", use_container_width=True):
            if os.path.exists(ARCH_METAS): os.remove(ARCH_METAS); st.rerun()

    # --- BOTÓN DE SALIDA ---
    st.write("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.usuario_logeado = None
        st.rerun()
