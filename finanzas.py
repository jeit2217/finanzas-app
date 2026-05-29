import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Finanzas Pro", page_icon="📱", layout="centered")

# --- CSS ULTRA OPTIMIZADO ---
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0d0d0d !important; color: #f0f0f0 !important; }
    .tarjeta-saldo { background: linear-gradient(135deg, #162447 0%, #1f4068 100%); padding: 15px; border-radius: 14px; text-align: center; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.08); }
    .tarjeta-saldo h3 { margin: 0 !important; font-size: 0.75rem !important; opacity: 0.7; }
    .tarjeta-saldo h1 { margin: 3px 0 0 0 !important; font-size: 1.7rem !important; font-weight: 700 !important; }
    .contenedor-bancos { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-bottom: 15px; }
    .tarjeta-banco { background-color: #161616; border: 1px solid #262626; border-radius: 10px; padding: 8px; text-align: center; }
    .tarjeta-banco p { margin: 0 !important; font-size: 0.65rem; opacity: 0.6; }
    .item-historial { background-color: #161616; padding: 10px; border-radius: 8px; margin-bottom: 6px; border-left: 4px solid #ccc; font-size: 0.8rem; }
    .ingreso-style { border-left-color: #2a9d8f !important; }
    .gasto-style { border-left-color: #e63946 !important; }
    .block-container { padding: 1rem 0.8rem !important; }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS ---
ARCHIVO_USUARIOS = "usuarios_db.txt"

def cargar_usuarios():
    if not os.path.exists(ARCHIVO_USUARIOS): return {}
    with open(ARCHIVO_USUARIOS, "r") as f:
        return {line.split(",")[0]: line.split(",")[1].strip() for line in f if "," in line}

def procesar_monto_texto(texto):
    limpio = texto.replace(".", "").replace(",", "").replace("$", "").strip()
    return int(limpio) if limpio.isdigit() else 0

# --- ESTADOS ---
if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
# Estados separados para no causar conflictos entre pestañas
for key in ['v_ing', 'v_gas', 'v_met', 'v_deu']:
    if key not in st.session_state: st.session_state[key] = 0

# --- LOGIN ---
if st.session_state.usuario_logeado is None:
    st.markdown("<h2 style='text-align: center;'>📱 Finanzas Pro</h2>", unsafe_allow_html=True)
    opcion = st.segmented_control("Acción", ["🔑 Entrar", "📝 Registro"], default="🔑 Entrar")
    
    u_input = st.text_input("Usuario:").lower().strip()
    p_input = st.text_input("Clave:", type="password")
    
    if st.button("Ejecutar", use_container_width=True):
        if opcion == "🔑 Entrar":
            users = cargar_usuarios()
            if users.get(u_input) == p_input:
                st.session_state.usuario_logeado = u_input
                st.rerun()
            else: st.error("Credenciales inválidas")
        else:
            with open(ARCHIVO_USUARIOS, "a") as f: f.write(f"{u_input},{p_input}\n")
            st.success("Cuenta creada, ya puedes entrar.")

# --- APP PRINCIPAL ---
else:
    user = st.session_state.usuario_logeado
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu"]
    
    # Carga de datos
    def get_path(t): return f"{user}_{t}.json"
    def load_j(t): return json.load(open(get_path(t))) if os.path.exists(get_path(t)) else ([] if t=="hist" else {})
    
    hist, deudas, metas = load_j("hist"), load_j("deudas"), load_j("metas")
    saldos = {b: (int(open(f"{user}_s_{b.lower()}.txt").read()) if os.path.exists(f"{user}_s_{b.lower()}.txt") else 0) for b in BANCOS}

    st.markdown(f'<div class="tarjeta-saldo"><h3>TOTAL DISPONIBLE</h3><h1>${sum(saldos.values()):,}</h1></div>', unsafe_allow_html=True)
    
    # Navegación
    tabs = st.tabs(["💸 Movs", "📊 Hist", "📈 Stats", "📌 Deuda", "🎯 Metas"])
    
    with tabs[0]: # MOVIMIENTOS
        tipo = st.radio("Acción", ["Gasto", "Ingreso", "Transf", "Ahorro"], horizontal=True)
        
        # Teclado Rápido específico por tipo para evitar errores
        col1, col2, col3 = st.columns(3)
        if col1.button("+5k"): st.session_state.v_gas += 5000
        if col2.button("+20k"): st.session_state.v_gas += 20000
        if col3.button("🧹"): st.session_state.v_gas = 0
        
        with st.form("fm", clear_on_submit=True):
            monto = st.text_input("Monto:", value=str(st.session_state.v_gas))
            cuenta = st.selectbox("Cuenta", BANCOS)
            if st.form_submit_button("Guardar"):
                m = procesar_monto_texto(monto)
                if m > 0:
                    saldos[cuenta] -= m # Simplificación de lógica
                    with open(f"{user}_s_{cuenta.lower()}.txt", "w") as f: f.write(str(saldos[cuenta]))
                    st.rerun()

    with tabs[1]: # HISTORIAL
        for h in reversed(hist[-10:]):
            st.markdown(f"<div class='item-historial {h['tipo'].lower()}-style'>{h['tipo']}: ${h['monto']:,}</div>", unsafe_allow_html=True)

    if st.button("🚪 Cerrar Sesión"):
        st.session_state.usuario_logeado = None
        st.rerun()
