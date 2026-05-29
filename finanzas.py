import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Finanzas Pro", page_icon="📱", layout="centered")

# --- CSS (Mismo que tenías, omitido aquí por brevedad, pero mantenlo en tu archivo) ---
# ... (Mantén tu bloque <style> original) ...

# --- LOGICA DE DATOS ---
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

# --- ESTADO INICIAL ---
if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
if 'val_express' not in st.session_state: st.session_state.val_express = 0

# --- LOGIN ---
if st.session_state.usuario_logeado is None:
    # ... (Tu lógica de login original aquí) ...
    pass
else:
    user = st.session_state.usuario_logeado
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu"]
    CATEGORIAS = ["Comida", "Transporte", "Rumba", "Deudas", "Hogar", "Otros"]
    
    ARCH_HIST = f"{user}_hist.json"
    ARCH_DEUDAS = f"{user}_deudas_v2.json"
    ARCH_METAS = f"{user}_metas.json"

    # ... (Funciones cargar_datos y guardar_datos originales) ...

    # --- PESTAÑA MOVIMIENTOS (Actualizada con validación) ---
    with tab_movs:
        tipo_mov = st.segmented_control("Transacción", ["📉 Gasto", "📈 Ingreso", "🔄 Transf.", "🎯 Ahorro Meta"], default="📉 Gasto")
        render_teclado_express(tipo_mov.lower()[:4])
        
        with st.form("form_movimiento_movil", clear_on_submit=True):
            b_origen = st.selectbox("¿De qué cuenta?", BANCOS)
            txt_monto = st.text_input("Monto:", value=f"{st.session_state.val_express:,}" if st.session_state.val_express > 0 else "", placeholder="$0")
            
            # Inputs condicionales
            paga_d = False
            id_d = ""
            if tipo_mov == "📉 Gasto":
                cat = st.selectbox("Categoría:", CATEGORIAS)
                paga_d = st.checkbox("¿Es abono a Deuda?")
                if paga_d: id_d = st.text_input("ID Deuda:").upper().strip()

            if st.form_submit_button(f"Confirmar {tipo_mov}"):
                monto = procesar_monto_texto(txt_monto)
                
                # --- VALIDACIÓN DE DEUDA ---
                if paga_d and id_d not in deudas:
                    st.error(f"❌ La deuda '{id_d}' no existe. Verifica el ID.")
                    st.stop() # Detiene la ejecución aquí
                
                if monto <= 0:
                    st.error("Monto inválido.")
                elif monto > saldos[b_origen]:
                    st.error("Saldo insuficiente.")
                else:
                    # Lógica de procesamiento de Gasto
                    if tipo_mov == "📉 Gasto":
                        if paga_d:
                            deudas[id_d]['monto_pendiente'] = max(0, deudas[id_d]['monto_pendiente'] - monto)
                            if deudas[id_d]['monto_pendiente'] == 0: deudas[id_d]['estado'] = "pagada"
                            guardar_datos("deudas", deudas)
                        
                        saldos[b_origen] -= monto
                        # Guardar saldos e historial...
                        st.session_state.val_express = 0
                        st.rerun()
                    # (Repetir lógica para Ingresos, Transferencias, etc.)
