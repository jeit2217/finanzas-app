import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Finanzas Pro", page_icon="📱", layout="centered")

# --- CSS PARA MÓVIL ---
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0d0d0d !important; color: #f0f0f0 !important; }
    .tarjeta-saldo { background: linear-gradient(135deg, #162447 0%, #1f4068 100%); padding: 15px; border-radius: 14px; text-align: center; margin-bottom: 12px; }
    .tarjeta-banco { background-color: #161616; border: 1px solid #262626; border-radius: 10px; padding: 8px; text-align: center; }
    .item-historial { background-color: #161616; padding: 10px; border-radius: 8px; margin-bottom: 6px; border-left: 4px solid #ccc; font-size: 0.85rem; }
    .gasto-style { border-left-color: #e63946 !important; }
    .ingreso-style { border-left-color: #2a9d8f !important; }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
def procesar_monto_texto(texto):
    limpio = texto.replace(".", "").replace(",", "").replace("$", "").strip()
    return int(limpio) if limpio.isdigit() else 0

if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
if 'val_express' not in st.session_state: st.session_state.val_express = 0

# --- LOGIN ---
if st.session_state.usuario_logeado is None:
    st.markdown("## 📱 Finanzas Pro")
    u_l = st.text_input("Usuario:").lower().strip()
    p_l = st.text_input("Clave:", type="password")
    if st.button("Ingresar"):
        if os.path.exists("usuarios_db.txt"):
            with open("usuarios_db.txt", "r") as f:
                for l in f:
                    p = l.strip().split(",")
                    if p[0] == u_l and p[1] == p_l:
                        st.session_state.usuario_logeado = u_l
                        st.rerun()
        st.error("Datos incorrectos")
else:
    user = st.session_state.usuario_logeado
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu"]
    CATEGORIAS = ["Comida", "Transporte", "Rumba", "Deudas", "Hogar", "Otros"]
    
    # Carga de archivos
    def get_data(file, default):
        if os.path.exists(file):
            with open(file, "r") as f: return json.load(f)
        return default

    hist = get_data(f"{user}_hist.json", [])
    deudas = get_data(f"{user}_deudas_v2.json", {})
    metas = get_data(f"{user}_metas.json", {})
    presupuestos = get_data(f"{user}_presupuestos.json", {cat: 0 for cat in CATEGORIAS})
    saldos = {b: int(open(f"{user}_s_{b.lower()}.txt", "r").read()) if os.path.exists(f"{user}_s_{b.lower()}.txt") else 0 for b in BANCOS}

    # --- UI ---
    st.markdown(f'<div class="tarjeta-saldo"><h3>TOTAL DISPONIBLE</h3><h1>${sum(saldos.values()):,}</h1></div>', unsafe_allow_html=True)
    
    tab_movs, tab_stats, tab_hist, tab_deudas = st.tabs(["💸", "📈", "📊", "📌"])

    with tab_movs:
        tipo = st.segmented_control("Acción", ["📉 Gasto", "📈 Ingreso"], default="📉 Gasto")
        
        # Teclado Rápido
        c1, c2, c3 = st.columns(3)
        for i, v in enumerate([2000, 10000, 50000]):
            if [c1, c2, c3][i].button(f"+${v//1000}k"): st.session_state.val_express += v
        if st.button("🧹 Limpiar Teclado"): st.session_state.val_express = 0

        with st.form("f_mov", clear_on_submit=True):
            b_o = st.selectbox("Cuenta:", BANCOS)
            txt_m = st.text_input("Monto:", value=str(st.session_state.val_express) if st.session_state.val_express > 0 else "")
            cat = st.selectbox("Categoría:", CATEGORIAS)
            paga_d = st.checkbox("¿Es abono a deuda?")
            id_d = st.text_input("ID Deuda (si aplica):").upper().strip()
            
            if st.form_submit_button("Confirmar"):
                m = procesar_monto_texto(txt_m)
                
                # VALIDACIÓN DEUDA
                if paga_d:
                    if id_d not in deudas:
                        st.error(f"❌ La deuda '{id_d}' no existe.")
                        st.stop()
                
                if m > 0 and m <= saldos[b_o]:
                    saldos[b_o] -= m
                    with open(f"{user}_s_{b_o.lower()}.txt", "w") as f: f.write(str(saldos[b_o]))
                    
                    if paga_d:
                        deudas[id_d]['monto_pendiente'] = max(0, deudas[id_d]['monto_pendiente'] - m)
                        with open(f"{user}_deudas_v2.json", "w") as f: json.dump(deudas, f)
                    
                    hist.append({"tipo": "Gasto", "banco": b_o, "monto": m, "cat": cat})
                    with open(f"{user}_hist.json", "w") as f: json.dump(hist, f)
                    st.session_state.val_express = 0
                    st.rerun()

    with tab_stats:
        df = pd.DataFrame(hist)
        with st.expander("⚙️ Límites Mensuales"):
            for cat in CATEGORIAS: presupuestos[cat] = st.number_input(f"Límite {cat}:", value=presupuestos.get(cat, 0))
            if st.button("Guardar"): json.dump(presupuestos, open(f"{user}_presupuestos.json", "w")); st.rerun()
        
        if not df.empty:
            for cat in CATEGORIAS:
                gastado = int(df[df['cat'] == cat]['monto'].sum())
                lim = presupuestos.get(cat, 0)
                if lim > 0:
                    porc = min(gastado / lim, 1.0)
                    color = "#e63946" if porc >= 1.0 else ("#e9c46a" if porc >= 0.7 else "#2a9d8f")
                    st.markdown(f"**{cat}**: ${gastado:,} / ${lim:,}")
                    st.markdown(f'<div style="background:{color}; height:8px; width:{porc*100}%; border-radius:4px;"></div>', unsafe_allow_html=True)
                    if porc >= 1.0: st.markdown("🚨 *¡Te quebraste!*")

    with tab_hist:
        for h in reversed(hist[-10:]):
            st.markdown(f"<div class='item-historial gasto-style'>{h['cat']}: ${h['monto']:,}</div>", unsafe_allow_html=True)
            
    if st.button("🚪 Cerrar Sesión"): st.session_state.usuario_logeado = None; st.rerun()
