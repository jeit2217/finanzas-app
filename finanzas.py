import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Finanzas Pro Stats", page_icon="💰", layout="centered")

# --- DISEÑO MÓVIL ---
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)
st.markdown("<style>.stApp { background-color: #121212 !important; color: #e0e0e0 !important; }</style>", unsafe_allow_html=True)

# Estilo de tarjetas optimizadas para pantallas angostas
st.markdown("<style>.tarjeta-saldo { background: linear-gradient(135deg, #1f4068 0%, #162447 100%); color: white !important; padding: 20px; border-radius: 16px; box-shadow: 0px 10px 25px rgba(0,0,0,0.15); text-align: center; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-saldo h3 {margin: 0 !important; font-size: 0.85rem !important; letter-spacing: 1px; opacity: 0.85; color: #f1faee !important;} .tarjeta-saldo h1 {margin: 5px 0 0 0 !important; font-size: 2.1rem !important; font-weight: 700 !important; color: #ffffff !important;}</style>", unsafe_allow_html=True)

st.markdown("<style>.tarjeta-gastos { background: linear-gradient(135deg, #781d1d 0%, #4a0e0e 100%); color: white !important; padding: 18px; border-radius: 16px; box-shadow: 0px 10px 25px rgba(0,0,0,0.15); text-align: center; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-gastos h3 {margin: 0 !important; font-size: 0.85rem !important; letter-spacing: 1px; opacity: 0.85; color: #f1faee !important;} .tarjeta-gastos h1 {margin: 5px 0 0 0 !important; font-size: 1.9rem !important; font-weight: 700 !important; color: #ffffff !important;}</style>", unsafe_allow_html=True)

st.markdown("<style>.contenedor-bancos {display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-bottom: 20px;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco {background-color: #1b1b1b; border: 1px solid #333; border-radius: 12px; padding: 10px; text-align: center; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco p {margin: 0 !important; font-size: 0.70rem; opacity: 0.7; text-transform: uppercase; font-weight: bold; letter-spacing: 0.5px;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco h4 {margin: 3px 0 0 0 !important; font-size: 0.95rem; font-weight: 700; color: #457b9d !important;}</style>", unsafe_allow_html=True)

st.markdown("<style>.item-historial { background-color: #1b1b1b; padding: 12px 15px; border-radius: 10px; margin-bottom: 8px; border-left: 5px solid #ccc; font-family: monospace; font-size: 0.85rem; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.ingreso-style { border-left-color: #2a9d8f !important; } .gasto-style { border-left-color: #e63946 !important; } .deuda-style { border-left-color: #f4a261 !important; } .pagada-style { border-left-color: #457b9d !important; } .meta-style { border-left-color: #a29bfe !important; }</style>", unsafe_allow_html=True)

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
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-weight: 800; font-size: 2rem;'>📱 Finanzas Pro</h1>", unsafe_allow_html=True)
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

    # --- PANTALLA FIJA SUPERIOR (Saldos siempre visibles) ---
    st.markdown(f'<div class="tarjeta-saldo"><h3>TOTAL GENERAL DISPONIBLE</h3><h1>${total_disponible:,} COP</h1></div>', unsafe_allow_html=True)
    cols_html = "".join([f'<div class="tarjeta-banco"><p>{b}</p><h4>${saldos[b]:,}</h4></div>' for b in BANCOS])
    st.markdown(f'<div class="contenedor-bancos">{cols_html}</div>', unsafe_allow_html=True)

    # --- 📱 NUEVO MENÚ ADAPTADO A CELULAR ---
    st.markdown("<p style='margin-bottom:0px; font-size:0.85rem; opacity:0.7; font-weight:bold;'>📍 NAVEGACIÓN APLICACIÓN:</p>", unsafe_allow_html=True)
    menu = st.selectbox(
        "Selecciona una pestaña:",
        ["📈 Estadísticas", "📊 Historial General", "💸 Registrar Movimientos", "📌 Control de Deudas", "🎯 Mis Metas"],
        label_visibility="collapsed"
    )
    st.write("---")

    # --- SECCIÓN 1: ESTADÍSTICAS ---
    if menu == "📈 Estadísticas":
        st.subheader("Resumen Analítico")
        df = pd.DataFrame(hist)
        total_gastado = 0
        if not df.empty and "Gasto" in df['tipo'].values:
            total_gastado = int(df[df['tipo'] == "Gasto"]['monto'].sum())
        st.markdown(f'<div class="tarjeta-gastos"><h3>GASTOS TOTALES ACUMULADOS</h3><h1>${total_gastado:,} COP</h1></div>', unsafe_allow_html=True)
        if total_gastado > 0:
            gastos_df = df[df['tipo'] == "Gasto"]
            resumen = gastos_df.groupby('cat')['monto'].sum()
            for cat, monto in resumen.items():
                porcentaje = (monto / total_gastado) * 100
                st.write(f"🔹 **{cat}:** ${int(monto):,} ({porcentaje:.1f}%)")
        else: st.info("No registras gastos todavía.")

    # --- SECCIÓN 2: HISTORIAL COMPLETO ---
    elif menu == "📊 Historial General":
        st.subheader("Lista de Movimientos")
        if len(hist) == 0: st.info("No hay transacciones.")
        else:
            for h in reversed(hist):
                if h['tipo'] == "Ingreso":
                    st.markdown(f'<div class="item-historial ingreso-style">📈 <b>Ingreso ({h["banco"]}):</b> +${h["monto"]:,} <br> 📝 {h["det"]}</div>', unsafe_allow_html=True)
                elif h['tipo'] == "Meta":
                    st.markdown(f'<div class="item-historial meta-style">🎯 <b>Ahorro Meta ({h["banco"]}):</b> -${h["monto"]:,} <br> 🚀 Para: {h["det"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="item-historial gasto-style">📉 <b>Gasto ({h["banco"]}):</b> -${h["monto"]:,} <br> 📁 {h["cat"]} | {h["det"]}</div>', unsafe_allow_html=True)
            st.write("---")
            if st.button("🗑️ Borrar Todo (Saldos y Movimientos)", use_container_width=True):
                for b in BANCOS:
                    if os.path.exists(f"{user}_s_{b.lower()}.txt"): os.remove(f"{user}_s_{b.lower()}.txt")
                if os.path.exists(ARCH_HIST): os.remove(ARCH_HIST)
                if os.path.exists(ARCH_METAS): os.remove(ARCH_METAS)
                st.rerun()

    # --- SECCIÓN 3: MOVIMIENTOS ---
    elif menu == "💸 Registrar Movimientos":
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("➕ Ingreso", use_container_width=True): st.session_state.modo = "ing"
        with c2:
            if st.button("➖ Gasto", use_container_width=True): st.session_state.modo = "gas"
        with c3:
            if st.button("🎯 Ahorro", use_container_width=True): st.session_state.modo = "meta"
        
        modo_actual = st.session_state.get('modo', 'ing')
        st.write("---")
        
        if modo_actual == "ing":
            st.markdown("### 📈 Añadir Fondos")
            b_i = st.selectbox("¿Cuenta?", BANCOS, key="sel_ing")
            m_i = st.number_input("Monto:", min_value=0, step=1000, key="num_ing")
            d_i = st.text_input("Detalle:", key="txt_ing")
            if st.button("Guardar Ingreso 📈", use_container_width=True):
                if m_i > 0:
                    saldos[b_i] += m_i
                    guardar_saldo(b_i, saldos[b_i])
                    hist.append({"tipo": "Ingreso", "banco": b_i, "monto": m_i, "cat": "Ingreso", "det": d_i if d_i else "Ingreso general"})
                    guardar_datos("hist", hist)
                    st.rerun()
        
        elif modo_actual == "gas":
            st.markdown("### 📉 Registrar Gasto")
            b_g = st.selectbox("¿Cuenta?", BANCOS, key="sel_gas")
            cat_g = st.selectbox("Categoría:", CATEGORIAS, key="sel_cat")
            m_g = st.number_input("Monto:", min_value=0, step=1000, key="num_gas")
            paga_d = st.checkbox("¿Paga deuda?")
            id_d = st.text_input("ID Deuda:").upper().strip() if paga_d else ""
            if st.button("Confirmar Gasto 📉", use_container_width=True):
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
                        else: st.error("ID inválido."); st.stop()
                    saldos[b_g] -= m_g
                    guardar_saldo(b_g, saldos[b_g])
                    hist.append({"tipo": "Gasto", "banco": b_g, "monto": m_g, "cat": cat_g, "det": f"Abono ID: {id_d}" if paga_d else f"Gasto: {cat_g}"})
                    guardar_datos("hist", hist)
                    st.rerun()
                elif m_g > saldos[b_g]: st.error("Saldo insuficiente.")
        
        elif modo_actual == "meta":
            st.markdown("### 🎯 Guardar para una Meta")
            if not metas:
                st.warning("Primero crea una meta en la pestaña 🎯 Mis Metas")
            else:
                b_m = st.selectbox("¿De qué cuenta sale el ahorro?", BANCOS, key="sel_b_meta")
                meta_dest = st.selectbox("¿Para qué meta es?", list(metas.keys()))
                m_m = st.number_input("Monto a ahorrar:", min_value=0, step=1000)
                if st.button("Confirmar Ahorro 🚀", use_container_width=True):
                    if m_m > 0 and m_m <= saldos[b_m]:
                        saldos[b_m] -= m_m
                        guardar_saldo(b_m, saldos[b_m])
                        metas[meta_dest]['ahorrado'] += m_m
                        guardar_datos("metas", metas)
                        hist.append({"tipo": "Meta", "banco": b_m, "monto": m_m, "cat": "Ahorro", "det": meta_dest})
                        guardar_datos("hist", hist)
                        st.success(f"¡Ahorro para {meta_dest} registrado!")
                        st.rerun()
                    else: st.error("Saldo insuficiente.")

    # --- SECCIÓN 4: DEUDAS ---
    elif menu == "📌 Control de Deudas":
        st.subheader("Gestión de Deudas")
        id_n = st.text_input("ID Único Deuda:", placeholder="EJ: JUAN1").upper().strip()
        concepto_n = st.text_input("Concepto o Razón:")
        m_n = st.number_input("Monto Inicial:", min_value=0, step=1000)
        if st.button("Crear Deuda 📌", use_container_width=True):
            if id_n and m_n > 0 and concepto_n:
                if id_n in deudas: st.error("ID ya existe.")
                else:
                    deudas[id_n] = {"concepto": concepto_n, "monto_inicial": m_n, "monto_pendiente": m_n, "estado": "activa", "historial_pagos": [f"Creada por ${m_n:,}"]}
                    guardar_datos("deudas", deudas)
                    st.rerun()

        st.write("---")
        d_act = {k: v for k, v in deudas.items() if v.get('estado', 'activa') == "activa"}
        d_pag = {k: v for k, v in deudas.items() if v.get('estado', 'activa') == "pagada"}
        
        st.markdown("### 📋 Pendientes")
        for k, v in d_act.items():
            with st.expander(f"🔴 {k} | Pendiente: ${v['monto_pendiente']:,}"):
                st.write(f"**Concepto:** {v['concepto']}"); [st.write(f"• {p}") for p in v['historial_pagos']]
        
        st.write("---")
        st.markdown("### ✅ Pagadas")
        for k, v in d_pag.items():
            with st.expander(f"🟢 [PAGADA] {k}"):
                st.write(f"**Concepto:** {v['concepto']}"); [st.write(f"• {p}") for p in v['historial_pagos']]

        st.write("---")
        if st.button("🗑️ Limpiar Historial de Deudas", use_container_width=True):
            if os.path.exists(ARCH_DEUDAS): os.remove(ARCH_DEUDAS); st.rerun()

    # --- SECCIÓN 5: METAS ---
    elif menu == "🎯 Mis Metas":
        st.subheader("🎯 Objetivos de Ahorro")
        with st.expander("✨ Crear Nueva Meta"):
            nombre_m = st.text_input("¿Qué quieres comprar?", placeholder="Ej: PlayStation 6").strip()
            total_m = st.number_input("¿Cuánto cuesta?", min_value=0, step=50000)
            if st.button("Establecer Meta 🎯", use_container_width=True):
                if nombre_m and total_m > 0:
                    metas[nombre_m] = {"objetivo": total_m, "ahorrado": 0}
                    guardar_datos("metas", metas)
                    st.success(f"Meta '{nombre_m}' creada.")
                    st.rerun()

        st.write("---")
        if not metas: st.info("Aún no tienes metas creadas.")
        else:
            for m_nombre, m_datos in metas.items():
                progreso = m_datos['ahorrado'] / m_datos['objetivo']
                progreso = min(progreso, 1.0)
                
                st.markdown(f"#### {m_nombre}")
                st.write(f"💰 ${m_datos['ahorrado']:,} de ${m_datos['objetivo']:,} COP")
                st.progress(progreso)
                
                if progreso >= 1.0:
                    st.balloons()
                    st.success("¡META ALCANZADA! 🥳")
                
                if st.button(f"Eliminar Meta: {m_nombre}", key=f"del_{m_nombre}", use_container_width=True):
                    del metas[m_nombre]
                    guardar_datos("metas", metas)
                    st.rerun()

        st.write("---")
        if st.button("🗑️ Resetear todas las Metas", use_container_width=True):
            if os.path.exists(ARCH_METAS): os.remove(ARCH_METAS); st.rerun()

    # --- BOTÓN DE SALIDA INDEPENDIENTE AL FINAL ---
    st.write("---")
    if st.button("🚪 Salir de la Cuenta", use_container_width=True):
        st.session_state.usuario_logeado = None
        st.rerun()
