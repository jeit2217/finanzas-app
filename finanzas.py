import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA EMULACIÓN MÓVIL ---
st.set_page_config(page_title="Finanzas Pro", page_icon="📱", layout="centered")

# --- CSS ULTRA OPTIMIZADO PARA MÓVIL (PANTALLAS < 480px) ---
st.markdown("""
<style>
    /* Ocultar elementos innecesarios de escritorio */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Forzar fondo oscuro profundo y tipografía limpia */
    .stApp { background-color: #0d0d0d !important; color: #f0f0f0 !important; }
    
    /* Tarjetas de Saldo Compactas */
    .tarjeta-saldo {
        background: linear-gradient(135deg, #162447 0%, #1f4068 100%);
        padding: 15px;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 12px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .tarjeta-saldo h3 { margin: 0 !important; font-size: 0.75rem !important; letter-spacing: 0.5px; opacity: 0.7; color: #ffffff !important; }
    .tarjeta-saldo h1 { margin: 3px 0 0 0 !important; font-size: 1.7rem !important; font-weight: 700 !important; color: #ffffff !important; }

    /* Contenedor de Bancos en Cuadrícula Ajustada */
    .contenedor-bancos {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 6px;
        margin-bottom: 15px;
    }
    .tarjeta-banco {
        background-color: #161616;
        border: 1px solid #262626;
        border-radius: 10px;
        padding: 8px;
        text-align: center;
    }
    .tarjeta-banco p { margin: 0 !important; font-size: 0.65rem; opacity: 0.6; text-transform: uppercase; font-weight: bold; }
    .tarjeta-banco h4 { margin: 2px 0 0 0 !important; font-size: 0.85rem; font-weight: 700; color: #457b9d !important; }

    /* Historial Formato Lista de Notificaciones de Celular */
    .item-historial {
        background-color: #161616;
        padding: 10px 12px;
        border-radius: 8px;
        margin-bottom: 6px;
        border-left: 4px solid #ccc;
        font-size: 0.8rem;
    }
    .ingreso-style { border-left-color: #2a9d8f !important; }
    .gasto-style { border-left-color: #e63946 !important; }
    .deuda-style { border-left-color: #f4a261 !important; }
    .meta-style { border-left-color: #a29bfe !important; }
    .transferencia-style { border-left-color: #6c757d !important; }

    /* Ajuste de inputs para que no se vean gigantes */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        padding: 6px 10px !important;
        font-size: 0.9rem !important;
    }
    
    /* Quitar márgenes excesivos de Streamlit en móvil */
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; padding-left: 0.8rem !important; padding-right: 0.8rem !important; }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS Y LOGIC ---
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

# Inicialización de estados de teclado express
if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
if 'val_express' not in st.session_state: st.session_state.val_express = 0

# --- PANTALLA LOGIN DE UNA SOLA COLUMNA ---
if st.session_state.usuario_logeado is None:
    st.markdown("<h2 style='text-align: center; margin-top:20px; font-weight:800;'>📱 Finanzas Pro</h2>", unsafe_allow_html=True)
    opcion_login = st.segmented_control("Acción", ["🔑 Entrar", "📝 Registrarse"], default="🔑 Entrar")
    
    if opcion_login == "🔑 Entrar":
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

# --- INTERFAZ PRINCIPAL PARA MÓVIL ---
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

    saldos = {}
    for b in BANCOS:
        path_s = f"{user}_s_{b.lower()}.txt"
        saldos[b] = int(open(path_s, "r").read()) if os.path.exists(path_s) else 0

    hist = cargar_datos("hist")
    deudas = cargar_datos("deudas")
    metas = cargar_datos("metas")
    total_disponible = sum(saldos.values())

    # --- ENCABEZADO ULTRA COMPACTO ---
    st.markdown(f'<div class="tarjeta-saldo"><h3>DISPONIBLE TOTAL</h3><h1>${total_disponible:,}</h1></div>', unsafe_allow_html=True)
    cols_html = "".join([f'<div class="tarjeta-banco"><p>{b}</p><h4>${saldos[b]:,}</h4></div>' for b in BANCOS])
    st.markdown(f'<div class="contenedor-bancos">{cols_html}</div>', unsafe_allow_html=True)

    # --- PESTAÑAS SUPERIORES EN LUGAR DE SELECTBOX (Mucho más estético en celular) ---
    tab_movs, tab_hist, tab_stats, tab_deudas, tab_metas = st.tabs(["💸 + / -", "📊 Historial", "📈 Stats", "📌 Deudas", "🎯 Metas"])

    # --- FUNCIÓN REUTILIZABLE: TECLADO EXPRÉS VERTICAL/COMPACTO ---
    def render_teclado_express(key_prefix):
        st.markdown("<p style='font-size:0.75rem; margin-bottom:2px; opacity:0.6;'>⚡ Teclado Rápido:</p>", unsafe_allow_html=True)
        # Dividido en solo 2 filas de 3 columnas para que los botones sean grandes para el dedo
        f1_1, f1_2, f1_3 = st.columns(3)
        with f1_1: 
            if st.button("+$2k", key=f"{key_prefix}_2k", use_container_width=True): st.session_state.val_express += 2000
        with f1_2: 
            if st.button("+$5k", key=f"{key_prefix}_5k", use_container_width=True): st.session_state.val_express += 5000
        with f1_3: 
            if st.button("+$10k", key=f"{key_prefix}_10k", use_container_width=True): st.session_state.val_express += 10000
            
        f2_1, f2_2, f2_3 = st.columns(3)
        with f2_1: 
            if st.button("+$20k", key=f"{key_prefix}_20k", use_container_width=True): st.session_state.val_express += 20000
        with f2_2: 
            if st.button("+$50k", key=f"{key_prefix}_50k", use_container_width=True): st.session_state.val_express += 50000
        with f2_3: 
            if st.button("🧹 Limpiar", key=f"{key_prefix}_clr", use_container_width=True): st.session_state.val_express = 0

    # --- PESTAÑA 1: REGISTRAR MOVIMIENTOS ---
    with tab_movs:
        # Selector tipo pastilla/segmento para ahorrar espacio vertical
        tipo_mov = st.segmented_control("Transacción", ["📉 Gasto", "📈 Ingreso", "🔄 Transf.", "🎯 Ahorro Meta"], default="📉 Gasto")
        
        # El teclado express ahora es universal y comparte la memoria para no duplicar código
        render_teclado_express(tipo_mov.lower()[:4])
        val_inicial = f"{st.session_state.val_express:,}" if st.session_state.val_express > 0 else ""

        with st.form("form_movimiento_movil", clear_on_submit=True):
            b_origen = st.selectbox("¿De qué cuenta?", BANCOS)
            txt_monto = st.text_input("Monto:", value=val_inicial, placeholder="$0")
            
            if tipo_mov == "📉 Gasto":
                cat = st.selectbox("Categoría:", CATEGORIAS)
                det = st.text_input("Detalle (Opcional):")
                paga_d = st.checkbox("¿Es abono a Deuda?")
                id_d = st.text_input("ID Deuda:").upper().strip()
            elif tipo_mov == "📈 Ingreso":
                det = st.text_input("Origen del dinero:")
            elif tipo_mov == "🔄 Transf.":
                b_destino = st.selectbox("¿Cuenta destino?", BANCOS, key="dest_t")
            elif tipo_mov == "🎯 Ahorro Meta":
                meta_dest = st.selectbox("¿Para cuál objetivo?", list(metas.keys()) if metas else ["Sin Metas"])

            if st.form_submit_button(f"Confirmar {tipo_mov}", use_container_width=True):
                monto = procesar_monto_texto(txt_monto)
                if monto <= 0:
                    st.error("Monto inválido.")
                else:
                    # Lógica interna intacta
                    if tipo_mov == "📉 Gasto":
                        if monto <= saldos[b_origen]:
                            if paga_d and id_d in deudas:
                                deudas[id_d]['monto_pendiente'] = max(0, deudas[id_d]['monto_pendiente'] - monto)
                                deudas[id_d]['historial_pagos'].append(f"Abono de ${monto:,} desde {b_origen}")
                                if deudas[id_d]['monto_pendiente'] == 0: deudas[id_d]['estado'] = "pagada"
                                guardar_datos("deudas", deudas)
                            saldos[b_origen] -= monto
                            with open(f"{user}_s_{b_origen.lower()}.txt", "w") as f: f.write(str(saldos[b_origen]))
                            hist.append({"tipo": "Gasto", "banco": b_origen, "monto": monto, "cat": cat, "det": det if det else f"Gasto {cat}"})
                            guardar_datos("hist", hist)
                            st.session_state.val_express = 0
                            st.rerun()
                        else: st.error("Saldo insuficiente.")
                    
                    elif tipo_mov == "📈 Ingreso":
                        saldos[b_origen] += monto
                        with open(f"{user}_s_{b_origen.lower()}.txt", "w") as f: f.write(str(saldos[b_origen]))
                        hist.append({"tipo": "Ingreso", "banco": b_origen, "monto": monto, "cat": "Ingreso", "det": det if det else "Ingreso general"})
                        guardar_datos("hist", hist)
                        st.session_state.val_express = 0
                        st.rerun()
                        
                    elif tipo_mov == "🔄 Transf." and b_origen != b_destino:
                        if monto <= saldos[b_origen]:
                            saldos[b_origen] -= monto
                            saldos[b_destino] += monto
                            with open(f"{user}_s_{b_origen.lower()}.txt", "w") as f: f.write(str(saldos[b_origen]))
                            with open(f"{user}_s_{b_destino.lower()}.txt", "w") as f: f.write(str(saldos[b_destino]))
                            hist.append({"tipo": "Transferencia", "banco": b_origen, "monto": monto, "cat": b_destino, "det": f"Enviado a {b_destino}"})
                            guardar_datos("hist", hist)
                            st.session_state.val_express = 0
                            st.rerun()
                        else: st.error("Saldo insuficiente.")
                    
                    elif tipo_mov == "🎯 Ahorro Meta" and metas and meta_dest != "Sin Metas":
                        if monto <= saldos[b_origen]:
                            saldos[b_origen] -= monto
                            with open(f"{user}_s_{b_origen.lower()}.txt", "w") as f: f.write(str(saldos[b_origen]))
                            metas[meta_dest]['ahorrado'] += monto
                            guardar_datos("metas", metas)
                            hist.append({"tipo": "Meta", "banco": b_origen, "monto": monto, "cat": "Ahorro", "det": meta_dest})
                            guardar_datos("hist", hist)
                            st.session_state.val_express = 0
                            st.rerun()
                        else: st.error("Saldo insuficiente.")

    # --- PESTAÑA 2: HISTORIAL GENERAL COMPACTO ---
    with tab_hist:
        if not hist: st.info("Sin transacciones.")
        else:
            # Mostrar solo los últimos 15 para evitar scrolls eternos que congelen el móvil
            for h in reversed(hist[-15:]):
                t_style = h['tipo'].lower()
                icon = "📈" if h['tipo'] == "Ingreso" else ("📉" if h['tipo'] == "Gasto" else ("🔄" if h['tipo'] == "Transferencia" else "🎯"))
                signo = "+" if h['tipo'] == "Ingreso" else "-"
                
                st.markdown(f"""
                <div class="item-historial {t_style}-style">
                    <b>{icon} {h['tipo']} ({h['banco']}):</b> {signo}${h['monto']:,}<br>
                    <span style='opacity:0.7; font-size:0.75rem;'>{h.get('cat','')} | {h['det']}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.write("---")
            with st.expander("🚨 Opciones de Borrado"):
                if st.button("🗑️ Resetear App por Completo", use_container_width=True):
                    for b in BANCOS:
                        if os.path.exists(f"{user}_s_{b.lower()}.txt"): os.remove(f"{user}_s_{b.lower()}.txt")
                    if os.path.exists(ARCH_HIST): os.remove(ARCH_HIST)
                    if os.path.exists(ARCH_METAS): os.remove(ARCH_METAS)
                    if os.path.exists(ARCH_DEUDAS): os.remove(ARCH_DEUDAS)
                    st.rerun()

    # --- PESTAÑA 3: ESTADÍSTICAS ---
    with tab_stats:
        df = pd.DataFrame(hist)
        total_gastado = int(df[df['tipo'] == "Gasto"]['monto'].sum()) if not df.empty and "Gasto" in df['tipo'].values else 0
        
        st.markdown(f'<div class="tarjeta-saldo" style="background: #4a0e0e;"><h3>GASTO TOTAL DEL MES</h3><h1>${total_gastado:,}</h1></div>', unsafe_allow_html=True)
        
        if total_gastado > 0:
            resumen = df[df['tipo'] == "Gasto"].groupby('cat')['monto'].sum()
            for cat, monto in resumen.items():
                porcentaje = (monto / total_gastado) * 100
                st.write(f"🔹 **{cat}:** ${int(monto):,} ({porcentaje:.1f}%)")
                st.progress(min(porcentaje / 100, 1.0))
        else: st.info("No hay gastos analizados.")

    # --- PESTAÑA 4: DEUDAS COMPACTAS ---
    with tab_deudas:
        with st.expander("➕ Registrar Nueva Deuda"):
            render_teclado_express("crear_deu")
            v_deu_ini = f"{st.session_state.val_express:,}" if st.session_state.val_express > 0 else ""
            with st.form("f_deuda_movil", clear_on_submit=True):
                id_n = st.text_input("Código Corto (Ej: PEPE):").upper().strip()
                concepto_n = st.text_input("¿Por qué?")
                txt_m_n = st.text_input("Monto Deuda:", value=v_deu_ini)
                if st.form_submit_button("Crear 📌", use_container_width=True):
                    m_n = procesar_monto_texto(txt_m_n)
                    if id_n and m_n > 0 and concepto_n:
                        deudas[id_n] = {"concepto": concepto_n, "monto_inicial": m_n, "monto_pendiente": m_n, "estado": "activa", "historial_pagos": [f"Creada por ${m_n:,}"]}
                        guardar_datos("deudas", deudas)
                        st.session_state.val_express = 0
                        st.rerun()

        st.markdown("##### 📋 Cuentas Pendientes")
        for k, v in deudas.items():
            if v.get('estado', 'activa') == "activa":
                with st.expander(f"🔴 {k} | Debe: ${v['monto_pendiente']:,}"):
                    st.caption(f"Motivo: {v['concepto']}")
                    for p in v['historial_pagos']: st.caption(f"• {p}")

    # --- PESTAÑA 5: METAS DE AHORRO ---
    with tab_metas:
        with st.expander("➕ Establecer Nuevo Objetivo"):
            render_teclado_express("crear_meta")
            v_meta_ini = f"{st.session_state.val_express:,}" if st.session_state.val_express > 0 else ""
            with st.form("f_meta_movil", clear_on_submit=True):
                nombre_m = st.text_input("¿Qué quieres lograr?").strip()
                txt_total_m = st.text_input("¿Cuánto necesitas?:", value=v_meta_ini)
                if st.form_submit_button("Fijar Meta 🎯", use_container_width=True):
                    total_m = procesar_monto_texto(txt_total_m)
                    if nombre_m and total_m > 0:
                        metas[nombre_m] = {"objetivo": total_m, "ahorrado": 0}
                        guardar_datos("metas", metas)
                        st.session_state.val_express = 0
                        st.rerun()

        for m_nombre, m_datos in list(metas.items()):
            progreso = min(m_datos['ahorrado'] / m_datos['objetivo'], 1.0) if m_datos['objetivo'] > 0 else 0
            st.markdown(f"**{m_nombre}** (${m_datos['ahorrado']:,} de ${m_datos['objetivo']:,})")
            st.progress(progreso)
            if progreso >= 1.0: st.success("¡Completado! 🎉")
            if st.button("❌ Quitar", key=f"del_{m_nombre}", size="small"):
                del metas[m_nombre]
                guardar_datos("metas", metas)
                st.rerun()

    # --- BOTÓN DE SALIDA DISCRETO ---
    st.write("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.usuario_logeado = None
        st.rerun()
