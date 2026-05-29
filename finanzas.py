import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA EMULACIÓN MÓVIL ---
st.set_page_config(page_title="Finanzas Pro", page_icon="📱", layout="centered")

# --- CSS ULTRA OPTIMIZADO PARA MÓVIL ---
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0d0d0d !important; color: #f0f0f0 !important; }
    .tarjeta-saldo { background: linear-gradient(135deg, #162447 0%, #1f4068 100%); padding: 15px; border-radius: 14px; text-align: center; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.08); }
    .tarjeta-saldo h3 { margin: 0 !important; font-size: 0.75rem !important; opacity: 0.7; color: #ffffff !important; }
    .tarjeta-saldo h1 { margin: 3px 0 0 0 !important; font-size: 1.7rem !important; font-weight: 700 !important; color: #ffffff !important; }
    .contenedor-bancos { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-bottom: 15px; }
    .tarjeta-banco { background-color: #161616; border: 1px solid #262626; border-radius: 10px; padding: 8px; text-align: center; }
    .tarjeta-banco p { margin: 0 !important; font-size: 0.65rem; opacity: 0.6; text-transform: uppercase; font-weight: bold; }
    .tarjeta-banco h4 { margin: 2px 0 0 0 !important; font-size: 0.85rem; font-weight: 700; color: #457b9d !important; }
    .item-historial { background-color: #161616; padding: 10px 12px; border-radius: 8px; margin-bottom: 6px; border-left: 4px solid #ccc; font-size: 0.8rem; }
    .ingreso-style { border-left-color: #2a9d8f !important; }
    .gasto-style { border-left-color: #e63946 !important; }
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

if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
if 'val_express' not in st.session_state: st.session_state.val_express = 0

# --- LOGIN ---
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
else:
    user = st.session_state.usuario_logeado
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu"]
    CATEGORIAS = ["Comida", "Transporte", "Rumba", "Deudas", "Hogar", "Otros"]
    ARCH_HIST, ARCH_DEUDAS, ARCH_METAS = f"{user}_hist.json", f"{user}_deudas_v2.json", f"{user}_metas.json"

    def cargar_datos(tipo):
        p = ARCH_HIST if tipo == "hist" else (ARCH_DEUDAS if tipo == "deudas" else ARCH_METAS)
        if os.path.exists(p):
            with open(p, "r") as f: return json.load(f)
        return [] if tipo == "hist" else {}

    def guardar_datos(tipo, d):
        p = ARCH_HIST if tipo == "hist" else (ARCH_DEUDAS if tipo == "deudas" else ARCH_METAS)
        with open(p, "w") as f: json.dump(d, f)

    saldos = {b: int(open(f"{user}_s_{b.lower()}.txt", "r").read()) if os.path.exists(f"{user}_s_{b.lower()}.txt") else 0 for b in BANCOS}
    hist, deudas, metas = cargar_datos("hist"), cargar_datos("deudas"), cargar_datos("metas")

    # --- UI ---
    st.markdown(f'<div class="tarjeta-saldo"><h3>DISPONIBLE TOTAL</h3><h1>${sum(saldos.values()):,}</h1></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="contenedor-bancos">{"".join([f"<div class=\'tarjeta-banco\'><p>{b}</p><h4>${saldos[b]:,}</h4></div>" for b in BANCOS])}</div>', unsafe_allow_html=True)

    tab_movs, tab_hist, tab_stats, tab_deudas, tab_metas = st.tabs(["💸 + / -", "📊 Historial", "📈 Stats", "📌 Deudas", "🎯 Metas"])

    # --- PESTAÑA 1: MOVIMIENTOS ---
    with tab_movs:
        tipo_mov = st.segmented_control("Transacción", ["📉 Gasto", "📈 Ingreso", "🔄 Transf.", "🎯 Ahorro Meta"], default="📉 Gasto")
        with st.form("form_movimiento_movil", clear_on_submit=True):
            b_origen = st.selectbox("¿De qué cuenta?", BANCOS)
            txt_monto = st.text_input("Monto:", placeholder="$0")
            
            paga_d = False
            id_d = ""
            if tipo_mov == "📉 Gasto":
                cat = st.selectbox("Categoría:", CATEGORIAS)
                paga_d = st.checkbox("¿Es abono a Deuda?")
                if paga_d: id_d = st.text_input("ID Deuda:").upper().strip()
            
            if st.form_submit_button("Confirmar"):
                monto = procesar_monto_texto(txt_monto)
                # Validación de deuda
                if paga_d:
                    if id_d not in deudas:
                        st.error(f"❌ La deuda '{id_d}' no existe.")
                        st.stop()
                
                if monto <= 0 or monto > saldos[b_origen]:
                    st.error("Monto inválido o saldo insuficiente.")
                else:
                    if tipo_mov == "📉 Gasto":
                        if paga_d:
                            deudas[id_d]['monto_pendiente'] = max(0, deudas[id_d]['monto_pendiente'] - monto)
                            guardar_datos("deudas", deudas)
                        saldos[b_origen] -= monto
                        with open(f"{user}_s_{b_origen.lower()}.txt", "w") as f: f.write(str(saldos[b_origen]))
                        hist.append({"tipo": "Gasto", "banco": b_origen, "monto": monto, "cat": cat, "det": f"Pago Deuda {id_d}" if paga_d else "Gasto"})
                        guardar_datos("hist", hist)
                        st.rerun()

    # --- PESTAÑA 4: DEUDAS ---
    with tab_deudas:
        st.markdown("##### 📋 Cuentas Pendientes")
        for k, v in deudas.items():
            if v.get('estado', 'activa') == "activa":
                with st.expander(f"🔴 {k} | Debe: ${v['monto_pendiente']:,}"):
                    st.caption(f"Motivo: {v['concepto']}")
                    for p in v['historial_pagos']: st.caption(f"• {p}")

    # --- CIERRE ---
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.usuario_logeado = None
        st.rerun()
