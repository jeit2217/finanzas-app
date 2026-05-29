import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="Finanzas Pro 2026", page_icon="💰", layout="centered")

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stApp { background-color: #121212 !important; color: #e0e0e0 !important; }
    .tarjeta-saldo { background: linear-gradient(135deg, #1f4068 0%, #162447 100%); padding: 18px; border-radius: 14px; text-align: center; margin-bottom: 15px; }
    .cajon-prestamo { background-color: #102a43; border: 1px solid #1982c4; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
    .cajon-prestamo h4 { color: #9bccf8 !important; margin: 0; }
    .monto-deuda { font-size: 1.25rem; font-weight: bold; color: #ffadad; }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA BASE ---
if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None

if st.session_state.usuario_logeado is None:
    st.title("📱 Finanzas Pro")
    u_l = st.text_input("Usuario:").lower().strip()
    if st.button("Entrar"): st.session_state.usuario_logeado = u_l; st.rerun()
else:
    user = st.session_state.usuario_logeado
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu", "Guardado / Ahorro"]
    
    # Carga de datos simplificada
    def cargar(tipo): return json.load(open(f"{user}_{tipo}.json", "r")) if os.path.exists(f"{user}_{tipo}.json") else {}
    def guardar(tipo, d): json.dump(d, open(f"{user}_{tipo}.json", "w"))

    prestamos = cargar("prestamos") # Estructura esperada: {id: {"nombre": "X", "saldo": 0, "tasa": 0.0, "pago_min": 0}}
    
    # --- PESTAÑAS ---
    _, _, tab_pre = st.tabs(["Dashboard", "Historial", "🤝 Acelerador de Deudas"])

    with tab_pre:
        st.subheader("🔥 Acelerador de Deudas (Método Avalancha)")
        
        # 1. Registrar Deuda
        with st.expander("➕ Nueva Deuda"):
            with st.form("form_deuda"):
                nombre = st.text_input("Nombre (ej. Tarjeta Nu)")
                saldo = st.number_input("Saldo Pendiente", min_value=0)
                tasa = st.number_input("Tasa Interés Mensual (%)", min_value=0.0)
                pago_min = st.number_input("Pago Mínimo Mensual", min_value=0)
                if st.form_submit_button("Guardar"):
                    prestamos[nombre] = {"nombre": nombre, "saldo": saldo, "tasa": tasa, "pago_min": pago_min}
                    guardar("prestamos", prestamos); st.rerun()

        # 2. Lógica del Optimizador
        if prestamos:
            df = pd.DataFrame(prestamos).T.sort_values(by='tasa', ascending=False)
            st.table(df[['nombre', 'saldo', 'tasa', 'pago_min']])
            
            # 3. Recomendación
            presupuesto_extra = st.number_input("¿Cuánto dinero extra puedes inyectar hoy?", min_value=0)
            
            if presupuesto_extra > 0:
                objetivo = df.iloc[0] # La deuda más cara
                pago_total = objetivo['pago_min'] + presupuesto_extra
                
                # Cálculo simplificado de meses ahorrados
                meses_original = objetivo['saldo'] / objetivo['pago_min'] if objetivo['pago_min'] > 0 else 999
                meses_nuevo = objetivo['saldo'] / pago_total
                ahorro = meses_original - meses_nuevo
                
                st.warning(f"💡 **Recomendación Estratégica**")
                st.write(f"Si inyectas **${presupuesto_extra:,}** a **{objetivo['nombre']}**:")
                st.success(f"✅ Terminarás esta deuda **{ahorro:.1f} meses antes**.")
                
                if st.button("Aplicar Pago"):
                    prestamos[objetivo['nombre']]['saldo'] -= presupuesto_extra
                    guardar("prestamos", prestamos); st.rerun()
        else:
            st.info("No tienes deudas registradas. ¡Excelente trabajo! 😎")

    if st.button("Cerrar Sesión"):
        st.session_state.usuario_logeado = None
        st.rerun()
