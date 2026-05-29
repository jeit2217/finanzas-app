import streamlit as st
import os
import json

# --- ARCHIVOS DE BASE DE DATOS ---
ARCHIVO_USUARIOS = "usuarios_db.txt"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Finanzas Pro", page_icon="💰", layout="centered")

# --- DISEÑO VISUAL BASE ---
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} .stAppDeployButton {display:none;}</style>", unsafe_allow_html=True)
st.markdown("<style>.stApp { background-color: #121212 !important; color: #e0e0e0 !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>h1, h2, h3, h4, p, label, .stMarkdown { color: #e0e0e0 !important; }</style>", unsafe_allow_html=True)

# Estilos de Tarjetas
st.markdown("<style>.tarjeta-saldo { background: linear-gradient(135deg, #1f4068 0%, #162447 100%); color: white !important; padding: 25px; border-radius: 16px; box-shadow: 0px 10px 25px rgba(0,0,0,0.15); text-align: center; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-saldo h3 {margin: 0 !important; font-size: 0.90rem !important; letter-spacing: 1.5px; opacity: 0.85; color: #f1faee !important;} .tarjeta-saldo h1 {margin: 8px 0 0 0 !important; font-size: 2.4rem !important; font-weight: 700 !important; color: #ffffff !important;}</style>", unsafe_allow_html=True)
st.markdown("<style>.contenedor-bancos {display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 25px;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco {background-color: #1b1b1b; border: 1px solid #333; border-radius: 12px; padding: 12px; text-align: center; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco p {margin: 0 !important; font-size: 0.75rem; opacity: 0.7; text-transform: uppercase; font-weight: bold; letter-spacing: 0.5px;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco h4 {margin: 5px 0 0 0 !important; font-size: 1.0rem; font-weight: 700; color: #457b9d !important;}</style>", unsafe_allow_html=True)

# Historial y deudas
st.markdown("<style>.item-historial { background-color: #1b1b1b; color: #e0e0e0; border: 1px solid #333; padding: 14px 18px; border-radius: 10px; margin-bottom: 10px; border-left: 6px solid #ccc; font-family: monospace; font-size: 0.95rem;}</style>", unsafe_allow_html=True)
st.markdown("<style>.ingreso-style { border-left-color: #2a9d8f !important; } .gasto-style { border-left-color: #e63946 !important; } .deuda-style { border-left-color: #f4a261 !important; }</style>", unsafe_allow_html=True)

# --- FUNCIONES DE CONTROL DE ACCESO ---
def cargar_usuarios():
    usuarios = {}
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, "r") as archivo:
            for linea in archivo:
                partes = linea.strip().split(",")
                if len(partes) == 2: usuarios[partes[0]] = partes[1]
    return usuarios

def registrar_usuario(nuevo_usuario, nueva_contrasena):
    with open(ARCHIVO_USUARIOS, "a") as archivo: archivo.write(f"{nuevo_usuario},{nueva_contrasena}\n")

if 'usuario_logeado' not in st.session_state:
    st.session_state.usuario_logeado = None

# --- ACCESO ---
if st.session_state.usuario_logeado is None:
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>📱 Finanzas Pro</h1>", unsafe_allow_html=True)
    pest_login, pest_reg = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
    
    with pest_reg:
        r_user = st.text_input("Usuario:", key="r_u").lower().strip()
        r_pass = st.text_input("Contraseña:", type="password", key="r_p").strip()
        if st.button("Crear Cuenta ✨", use_container_width=True):
            us_ex = cargar_usuarios()
            if r_user and r_pass:
                if r_user in us_ex: st.error("Usuario ya existe.")
                else:
                    registrar_usuario(r_user, r_pass)
                    st.success("¡Cuenta creada!")
            else: st.warning("Completa los campos.")

    with pest_login:
        l_user = st.text_input("Usuario:", key="l_u").lower().strip()
        l_pass = st.text_input("Contraseña:", type="password", key="l_p").strip()
        if st.button("Ingresar 🚀", use_container_width=True):
            us_ex = cargar_usuarios()
            if l_user in us_ex and us_ex[l_user] == l_pass:
                st.session_state.usuario_logeado = l_user
                st.rerun()
            else: st.error("Datos incorrectos.")

# --- APP ADENTRO ---
else:
    user = st.session_state.usuario_logeado
    ARCHIVO_HISTORIAL = f"{user}_historial.txt"
    ARCHIVO_DEUDAS = f"{user}_deudas.json"
    BANCOS = ["Efectivo", "Nequi", "Daviplata", "Nu"]

    # Funciones de carga y guardado individuales
    def cargar_saldo(b):
        path = f"{user}_saldo_{b.lower()}.txt"
        if os.path.exists(path):
            with open(path, "r") as f:
                try: return int(f.read())
                except: return 0
        return 0

    def guardar_saldo(b, s):
        with open(f"{user}_saldo_{b.lower()}.txt", "w") as f: f.write(str(s))

    def mov(t):
        with open(ARCHIVO_HISTORIAL, "a") as f: f.write(t + "\n")

    def cargar_deudas():
        if os.path.exists(ARCHIVO_DEUDAS):
            with open(ARCHIVO_DEUDAS, "r") as f:
                try: return json.load(f)
                except: return {}
        return {}

    def guardar_deudas(d):
        with open(ARCHIVO_DEUDAS, "w") as f: json.dump(d, f, indent=4)

    # Cargar Datos Iniciales
    saldos = {b: cargar_saldo(b) for b in BANCOS}
    total_gral = sum(saldos.values())
    deudas = cargar_deudas()

    if st.button("🚪 Salir"):
        st.session_state.usuario_logeado = None
        st.rerun()

    # --- PANTALLA VISUAL DE SALDOS ---
    st.markdown(f'<div class="tarjeta-saldo"><h3>TOTAL GENERAL DISPONIBLE</h3><h1>${total_gral:,} COP</h1></div>', unsafe_allow_html=True)
    cols_html = "".join([f'<div class="tarjeta-banco"><p>{b}</p><h4>${saldos[b]:,}</h4></div>' for b in BANCOS])
    st.markdown(f'<div class="contenedor-bancos">{cols_html}</div>', unsafe_allow_html=True)

    # --- NUEVAS PESTAÑAS (INCLUYENDO DEUDAS) ---
    p_panel, p_ing, p_gas, p_deu = st.tabs(["📊 Historial", "📈 Ingreso", "📉 Gasto", "📌 Deudas"])

    # --- HISTORIAL ---
    with p_panel:
        if os.path.exists(ARCHIVO_HISTORIAL):
            with open(ARCHIVO_HISTORIAL, "r") as f:
                lineas = f.readlines()
                if lineas:
                    for l in reversed(lineas):
                        clase = "ingreso-style" if "📈" in l else ("deuda-style" if "📌" in l else "gasto-style")
                        st.markdown(f'<div class="item-historial {clase}">{l.strip()}</div>', unsafe_allow_html=True)
                    st.write("---")
                    if st.button("🗑 Presionar para Borrar Todo"):
                        for b in BANCOS:
                            if os.path.exists(f"{user}_saldo_{b.lower()}.txt"): os.remove(f"{user}_saldo_{b.lower()}.txt")
                        if os.path.exists(ARCHIVO_HISTORIAL): os.remove(ARCHIVO_HISTORIAL)
                        if os.path.exists(ARCHIVO_DEUDAS): os.remove(ARCHIVO_DEUDAS)
                        st.rerun()
                else: st.info("No hay movimientos.")
        else: st.info("No hay movimientos.")

    # --- INGRESOS ---
    with p_ing:
        b_dest = st.selectbox("¿A dónde entra la plata?", BANCOS, key="sel_b_ing")
        m_ing = st.number_input("Monto:", min_value=0, step=1000, key="num_m_ing")
        d_ing = st.text_input("Detalle (ej: Pago, Sueldo):", key="txt_d_ing")
        if st.button("Confirmar Ingreso"):
            if m_ing > 0:
                s_act = cargar_saldo(b_dest)
                guardar_saldo(b_dest, s_act + m_ing)
                mov(f"📈 {b_dest}: +${m_ing:,} ({d_ing if d_ing else 'Ingreso'})")
                st.rerun()

    # --- GASTOS (CON DESCUENTO INTELIGENTE DE DEUDA) ---
    with p_gas:
        b_ori = st.selectbox("¿De dónde sale la plata?", BANCOS, key="sel_b_gas")
        m_gas = st.number_input("Monto:", min_value=0, step=1000, key="num_m_gas")
        d_gas = st.text_input("Detalle (ej: Almuerzo, Abono):", key="txt_d_gas")
        
        # Preguntar si el gasto paga una deuda
        paga_deuda = st.checkbox("¿Este gasto descuenta o paga una deuda activa?")
        id_deuda_ingresado = ""
        if paga_deuda:
            id_deuda_ingresado = st.text_input("Escribe el CODIGO ID de la deuda:", placeholder="Ej: JUAN01").strip().upper()

        if st.button("Registrar Gasto"):
            s_act = cargar_saldo(b_ori)
            if m_gas > 0 and m_gas <= s_act:
                
                # Si el usuario dice que paga una deuda, validar ID
                if paga_deuda:
                    if id_deuda_ingresado not in deudas:
                        st.error("❌ El Código ID ingresado no coincide con ninguna deuda activa.")
                    else:
                        # Descontar saldo de la deuda
                        deudas[id_deuda_ingresado]["monto"] -= m_gas
                        nombre_deuda = deudas[id_deuda_ingresado]["nombre"]
                        
                        # Si la deuda queda saldada, se elimina
                        if deudas[id_deuda_ingresado]["monto"] <= 0:
                            detalle_pago = f"Abono final - ¡Deuda Saldada!"
                            del deudas[id_deuda_ingresado]
                        else:
                            detalle_pago = f"Abono a deuda {nombre_deuda} (Faltan: ${deudas[id_deuda_ingresado]['monto']:,})"
                        
                        guardar_deudas(deudas)
                        guardar_saldo(b_ori, s_act - m_gas)
                        mov(f"📉 {b_ori}: -${m_gas:,} ({d_gas if d_gas else detalle_pago})")
                        st.rerun()
                else:
                    # Gasto normal sin deudas
                    guardar_saldo(b_ori, s_act - m_gas)
                    mov(f"📉 {b_ori}: -${m_gas:,} ({d_gas if d_gas else 'Gasto'})")
                    st.rerun()
                    
            elif m_gas > s_act: st.warning("Fondos insuficientes en esta cuenta.")

    # --- NUEVA PESTAÑA: GESTIÓN DE DEUDAS ---
    with p_deu:
        st.markdown("### 📌 Crear Nueva Deuda")
        id_nueva = st.text_input("Crea un CODIGO ID único (Sin espacios):", placeholder="Ej: JUAN01").strip().upper()
        nombre_nueva = st.text_input("¿A quién o qué le debes?:", placeholder="Ej: Prestamo Juan, Cuota Moto")
        monto_nueva = st.number_input("Monto total de la deuda:", min_value=0, step=1000)
        
        if st.button("Registrar Deuda 📌"):
            if id_nueva and nombre_nueva and monto_nueva > 0:
                if id_nueva in deudas:
                    st.error("❌ Este Código ID ya existe. Elige otro diferente.")
                else:
                    deudas[id_nueva] = {"nombre": nombre_nueva, "monto": monto_nueva}
                    guardar_deudas(deudas)
                    mov(f"📌 Deuda Creada [{id_nueva}]: {nombre_nueva} por ${monto_nueva:,}")
                    st.success(f"✅ Deuda registrada con el ID: {id_nueva}")
                    st.rerun()
            else:
                st.warning("Por favor rellena todos los datos.")
                
        st.write("---")
        st.markdown("### 📋 Tus Deudas Activas")
        if deudas:
            for i_d, info in deudas.items():
                st.markdown(
                    f"""
                    <div class="item-historial deuda-style">
                        <b>🆔 ID: {i_d}</b><br>
                        📌 Concepto: {info['nombre']}<br>
                        💰 Saldo Pendiente: <b style="color:#e63946;">${info['monto']:,} COP</b>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        else:
            st.info("🎉 ¡Felicidades! No tienes deudas registradas actualmente.")
