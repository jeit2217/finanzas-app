import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Finanzas Pro", page_icon="📱", layout="centered")

# --- CSS ---
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0d0d0d !important; color: #f0f0f0 !important; }
    .tarjeta-saldo { background: #162447; padding: 15px; border-radius: 14px; text-align: center; margin-bottom: 10px; }
    .item-historial { background: #161616; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 4px solid #457b9d; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE PERSISTENCIA ---
def asegurar_archivos(user):
    for b in ["Efectivo", "Nequi", "Daviplata", "Nu"]:
        path = f"{user}_s_{b.lower()}.txt"
        if not os.path.exists(path):
            with open(path, "w") as f: f.write("0")
    if not os.path.exists(f"{user}_hist.json"):
        with open(f"{user}_hist.json", "w") as f: json.dump([], f)

# --- INICIALIZACIÓN DE ESTADO ---
if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
if 'val_express' not in st.session_state: st.session_state.val_express = 0

# --- LOGIN ---
if st.session_state.usuario_logeado is None:
    st.title("📱 Finanzas Pro")
    u = st.text_input("Usuario:").lower().strip()
    p = st.text_input("Clave:", type="password")
    if st.button("Ingresar", use_container_width=True):
        if u and p:
            asegurar_archivos(u)
            st.session_state.usuario_logeado = u
            st.rerun()
else:
    # --- APP PRINCIPAL ---
    user = st.session_state.usuario_logeado
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu"]
    
    # Cargar saldos
    saldos = {}
    for b in BANCOS:
        path = f"{user}_s_{b.lower()}.txt"
        with open(path, "r") as f: saldos[b] = int(f.read())

    # Encabezado
    st.markdown(f'<div class="tarjeta-saldo"><h3>Total: ${sum(saldos.values()):,}</h3></div>', unsafe_allow_html=True)
    
    # Pestañas
    tab1, tab2 = st.tabs(["💸 Movimientos", "⚙️ Ajustes"])
    
    with tab1:
        st.write("### Registrar Gasto")
        monto = st.number_input("Monto", min_value=0, step=1000)
        banco = st.selectbox("Banco", BANCOS)
        if st.button("Confirmar Gasto"):
            if saldos[banco] >= monto:
                saldos[banco] -= monto
                with open(f"{user}_s_{banco.lower()}.txt", "w") as f: f.write(str(saldos[banco]))
                st.success("Guardado")
                st.rerun()
            else:
                st.error("Saldo insuficiente")

    with tab2:
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_logeado = None
            st.rerun()
