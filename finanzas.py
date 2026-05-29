import streamlit as st
import os
import json
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Finanzas Pro", page_icon="📱", layout="centered")

# --- CSS OPTIMIZADO PARA MÓVIL ---
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
    .meta-style { border-left-color: #a29bfe !important; }
    .transferencia-style { border-left-color: #6c757d !important; }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
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
    limpio = texto.replace(".", "").replace(",", "").replace("$", "").strip()
    return int(limpio) if limpio.isdigit() else 0

if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
if 'val_express' not in st.session_state: st.session_state.val_express = 0

# --- LOGIN ---
if st.session_state.usuario_logeado is None:
    st.markdown("<h2 style='text-align: center; margin-top:20px;'>📱 Finanzas Pro</h2>", unsafe_allow_html=True)
    if st.button("🔑 Entrar / Registrarse", use_container_width=True): st.rerun()
    u_l = st.text_input("Usuario:").lower().strip()
    p_l = st.text_input("Clave:", type="password")
    if st.button("Ingresar", use_container_width=True):
        users = cargar_usuarios()
        if u_l in users and users[u_l] == p_l:
            st.session_state.usuario_logeado = u_l
            st.rerun()
else:
    user = st.session_state.usuario_logeado
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu"]
    CATEGORIAS = ["Comida", "Transporte", "Rumba", "Deudas", "Hogar", "Otros"]
    
    # Rutas archivos
    ARCH_HIST = f"{user}_hist.json"
    ARCH_DEUDAS = f"{user}_deudas_v2.json"
    ARCH_METAS = f"{user}_metas.json"
    ARCH_PRESUPUESTOS = f"{user}_presupuestos.json"

    def cargar_datos(tipo):
        p = ARCH_HIST if tipo == "hist" else (ARCH_DEUDAS if tipo == "deudas" else ARCH_METAS)
        return json.load(open(p, "r")) if os.path.exists(p) else ([] if tipo == "hist" else {})

    def guardar_datos(tipo, d):
        p = ARCH_HIST if tipo == "hist" else (ARCH_DEUDAS if tipo == "deudas" else ARCH_METAS)
        with open(p, "w") as f: json.dump(d, f)

    def cargar_presupuestos():
        if os.path.exists(ARCH_PRESUPUESTOS): return json.load(open(ARCH_PRESUPUESTOS, "r"))
        return {cat: 0 for cat in CATEGORIAS}

    saldos = {b: int(open(f"{user}_s_{b.lower()}.txt", "r").read()) if os.path.exists(f"{user}_s_{b.lower()}.txt") else 0 for b in BANCOS}
    hist, deudas, metas = cargar_datos("hist"), cargar_datos("deudas"), cargar_datos("metas")

    # --- UI ---
    st.markdown(f'<div class="tarjeta-saldo"><h3>DISPONIBLE</h3><h1>${sum(saldos.values()):,}</h1></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="contenedor-bancos">{"".join([f"<div class=\'tarjeta-banco\'><p>{b}</p><h4>${saldos[b]:,}</h4></div>" for b in BANCOS])}</div>', unsafe_allow_html=True)

    tab_movs, tab_hist, tab_stats, tab_deudas, tab_metas = st.tabs(["💸", "📊", "📈", "📌", "🎯"])

    def render_teclado():
        cols = st.columns(3)
        for i, val in enumerate([2000, 5000, 10000, 20000, 50000, 0]):
            label = f"+${val//1000}k" if val > 0 else "🧹"
            if cols[i%3].button(label, use_container_width=True): st.session_state.val_express = st.session_state.val_express + val if val > 0 else 0

    with tab_movs:
        tipo = st.segmented_control("Acción", ["📉 Gasto", "📈 Ingreso", "🔄 Transf.", "🎯 Ahorro"], default="📉 Gasto")
        render_teclado()
        with st.form("form_f", clear_on_submit=True):
            b_o = st.selectbox("Cuenta:", BANCOS)
            txt_m = st.text_input("Monto:", value=str(st.session_state.val_express) if st.session_state.val_express > 0 else "")
            if st.form_submit_button("Confirmar"):
                m = procesar_monto_texto(txt_m)
                if m > 0 and m <= saldos[b_o]:
                    saldos[b_o] -= m
                    with open(f"{user}_s_{b_o.lower()}.txt", "w") as f: f.write(str(saldos[b_o]))
                    hist.append({"tipo": "Gasto", "banco": b_o, "monto": m, "cat": "Otros", "det": "Gasto"})
                    guardar_datos("hist", hist)
                    st.session_state.val_express = 0
                    st.rerun()

    with tab_stats:
        df = pd.DataFrame(hist)
        gastos = df[df['tipo'] == "Gasto"] if not df.empty else pd.DataFrame()
        presupuestos = cargar_presupuestos()
        
        with st.expander("⚙️ Límites Mensuales"):
            for cat in CATEGORIAS: presupuestos[cat] = st.number_input(f"Límite {cat}:", value=presupuestos.get(cat, 0), step=50000)
            if st.button("Guardar"): json.dump(presupuestos, open(ARCH_PRESUPUESTOS, "w")); st.rerun()
            
        if not gastos.empty:
            for cat in CATEGORIAS:
                gasto_cat = int(gastos[gastos['cat'] == cat]['monto'].sum())
                limite = presupuestos.get(cat, 0)
                if limite > 0:
                    porc = min(gasto_cat / limite, 1.0)
                    col = "#e63946" if porc >= 1.0 else ("#e9c46a" if porc >= 0.7 else "#2a9d8f")
                    st.markdown(f"**{cat}** (${gasto_cat:,} / ${limite:,})")
                    st.markdown(f'<div style="background:{col}; height:8px; width:{porc*100}%; border-radius:4px;"></div>', unsafe_allow_html=True)
                    if porc >= 1.0: st.caption("🚨 ¡Te quebraste!")

    with tab_hist:
        for h in reversed(hist[-10:]):
            st.markdown(f"<div class='item-historial {h['tipo'].lower()}-style'>{h['tipo']} ({h['banco']}): ${h['monto']:,}</div>", unsafe_allow_html=True)
