import streamlit as st
import os

# --- ARCHIVO BASE DE DATOS DE USUARIOS ---
ARCHIVO_USUARIOS = "usuarios_db.txt"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Finanzas Pro", page_icon="💰", layout="centered")

# --- DISEÑO VISUAL BASE (SIEMPRE MODO OSCURO AUTOMÁTICO) ---
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} .stAppDeployButton {display:none;}</style>", unsafe_allow_html=True)

# Forzar colores oscuros limpios en la interfaz
st.markdown("<style>.stApp { background-color: #121212 !important; color: #e0e0e0 !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>h1, h2, h3, h4, p, label, .stMarkdown { color: #e0e0e0 !important; }</style>", unsafe_allow_html=True)

# Tarjeta de saldo total (Grande)
st.markdown("<style>.tarjeta-saldo { background: linear-gradient(135deg, #1f4068 0%, #162447 100%); color: white !important; padding: 25px; border-radius: 16px; box-shadow: 0px 10px 25px rgba(0,0,0,0.15); text-align: center; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-saldo h3 {margin: 0 !important; font-size: 0.90rem !important; letter-spacing: 1.5px; opacity: 0.85; color: #f1faee !important;} .tarjeta-saldo h1 {margin: 8px 0 0 0 !important; font-size: 2.4rem !important; font-weight: 700 !important; color: #ffffff !important;}</style>", unsafe_allow_html=True)

# Tarjetas secundarias de bancos (Fila horizontal)
st.markdown("<style>.contenedor-bancos {display: flex; gap: 10px; justify-content: space-between; margin-bottom: 25px;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco {background-color: #1b1b1b; border: 1px solid #333; border-radius: 12px; padding: 12px; text-align: center; flex: 1; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco p {margin: 0 !important; font-size: 0.8rem; opacity: 0.7; text-transform: uppercase; font-weight: bold; letter-spacing: 0.5px;}</style>", unsafe_allow_html=True)
st.markdown("<style>.tarjeta-banco h4 {margin: 5px 0 0 0 !important; font-size: 1.1rem; font-weight: 700; color: #457b9d !important;}</style>", unsafe_allow_html=True)

# Historial
st.markdown("<style>.item-historial { background-color: #1b1b1b; color: #e0e0e0; border: 1px solid #333; padding: 14px 18px; border-radius: 10px; margin-bottom: 10px; border-left: 6px solid #ccc; box-shadow: 0px 4px 6px rgba(0,0,0,0.02); font-family: monospace; font-size: 0.95rem;}</style>", unsafe_allow_html=True)
st.markdown("<style>.ingreso-style { border-left-color: #2a9d8f !important; } .gasto-style { border-left-color: #e63946 !important; }</style>", unsafe_allow_html=True)

# --- FUNCIONES PARA EL SISTEMA DE USUARIOS ---
def cargar_usuarios():
    usuarios = {}
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, "r") as archivo:
            for linea in archivo:
                partes = linea.strip().split(",")
                if len(partes) == 2:
                    usuarios[partes[0]] = partes[1]
    return usuarios

def registrar_usuario(nuevo_usuario, nueva_contrasena):
    with open(ARCHIVO_USUARIOS, "a") as archivo:
        archivo.write(f"{nuevo_usuario},{nueva_contrasena}\n")

# --- INICIALIZAR MEMORIA DE SESIÓN ---
if 'usuario_logeado' not in st.session_state:
    st.session_state.usuario_logeado = None

# --- PANTALLA DE ACCESO (LOGIN / REGISTRO) ---
if st.session_state.usuario_logeado is None:
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>📱 Finanzas Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.7; margin-bottom: 30px;'>Tu control de gastos inteligente, privado y personalizado.</p>", unsafe_allow_html=True)
    
    pestaña_login, pestaña_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
    
    with pestaña_registro:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        reg_user = st.text_input("Elige tu usuario:", key="reg_user").lower().strip()
        reg_pass = st.text_input("Elige tu contraseña:", type="password", key="reg_pass").strip()
        
        if st.button("Crear Cuenta Nueva ✨", key="btn_registro", use_container_width=True):
            usuarios_existentes = cargar_usuarios()
            if reg_user == "" or reg_pass == "":
                st.warning("⚠️ Los campos no pueden estar vacíos.")
            elif reg_user in usuarios_existentes:
                st.error("❌ Este usuario ya existe.")
            else:
                registrar_usuario(reg_user, reg_pass)
                st.success("✅ ¡Cuenta creada! Pasa a la pestaña de 'Iniciar Sesión'.")

    with pestaña_login:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        login_user = st.text_input("Usuario:", key="login_user").lower().strip()
        login_pass = st.text_input("Contraseña:", type="password", key="login_pass").strip()
        
        if st.button("Ingresar de Forma Segura 🚀", key="btn_login", use_container_width=True):
            usuarios_existentes = cargar_usuarios()
            if login_user in usuarios_existentes and usuarios_existentes[login_user] == login_pass:
                st.session_state.usuario_logeado = login_user
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas. Verifica tus datos.")

# --- PANTALLA PRINCIPAL ADENTRO DE LA APP ---
else:
    user = st.session_state.usuario_logeado

    # Archivos independientes por usuario y banco
    ARCHIVO_HISTORIAL = f"{user}_historial.txt"
    
    def cargar_saldo_banco(banco):
        archivo_banco = f"{user}_saldo_{banco.lower()}.txt"
        if os.path.exists(archivo_banco):
            with open(archivo_banco, "r") as archivo:
                try:
                    return int(archivo.read())
                except:
                    return 0
        return 0

    def guardar_saldo_banco(banco, nuevo_saldo):
        archivo_banco = f"{user}_saldo_{banco.lower()}.txt"
        with open(archivo_banco, "w") as archivo:
            archivo.write(str(nuevo_saldo))

    def guardar_movimiento(texto):
        with open(ARCHIVO_HISTORIAL, "a") as archivo:
            archivo.write(texto + "\n")

    def cargar_historial():
        if os.path.exists(ARCHIVO_HISTORIAL):
            with open(ARCHIVO_HISTORIAL, "r") as archivo:
                return archivo.readlines()
        return []

    # Cargar saldos individuales de la base de datos
    saldo_nequi = cargar_saldo_banco("Nequi")
    saldo_daviplata = cargar_saldo_banco("Daviplata")
    saldo_nu = cargar_saldo_banco("Nu")
    
    # Calcular el gran total general
    saldo_total_general = saldo_nequi + saldo_daviplata + saldo_nu

    # Encabezado superior con botón de salida
    col_user, col_logout = st.columns([3, 1])
    with col_user:
        st.markdown(f"👤 Hola, <b style='color:#457b9d;'>{user.capitalize()}</b>", unsafe_allow_html=True)
    with col_logout:
        if st.button("🚪 Salir", use_container_width=True):
            st.session_state.usuario_logeado = None
            st.rerun()

    # --- TARJETA DE SALDO TOTAL GENERAL ---
    st.markdown(
        f"""
        <div class="tarjeta-saldo">
            <h3>TOTAL DISPONIBLE GENERAL</h3>
            <h1>${saldo_total_general:,} COP</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # --- FILA DE SALDOS POR BANCO ---
    st.markdown(
        f"""
        <div class="contenedor-bancos">
            <div class="tarjeta-banco">
                <p>📱 Nequi</p>
                <h4>${saldo_nequi:,}</h4>
            </div>
            <div class="tarjeta-banco">
                <p>🟥 Daviplata</p>
                <h4>${saldo_daviplata:,}</h4>
            </div>
            <div class="tarjeta-banco">
                <p>💜 Nu</p>
                <h4>${saldo_nu:,}</h4>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- MENÚ CENTRAL DE OPERACIONES ---
    pest_panel, pest_ingreso, pest_gasto = st.tabs(["📊 Panel General", "📈 Registrar Ingreso", "📉 Registrar Gasto"])

    # --- CONTENIDO PESTAÑA 1: HISTORIAL ---
    with pest_panel:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        lista_movimientos = cargar_historial()
        
        if len(lista_movimientos) == 0:
            st.info("No hay transacciones registradas todavía. Pasa a las siguientes pestañas para añadir movimientos.")
        else:
            for movimiento in reversed(lista_movimientos):
                texto = movimiento.strip()
                if "Ingreso" in texto:
                    st.markdown(f'<div class="item-historial ingreso-style">{texto}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="item-historial gasto-style">{texto}</div>', unsafe_allow_html=True)
            
            st.write("---")
            if st.button("🗑️ Borrar Todo el Historial", use_container_width=True, key="btn_borrar_todo"):
                # Eliminar todos los archivos de saldos y el historial
                for b in ["nequi", "daviplata", "nu"]:
                    if os.path.exists(f"{user}_saldo_{b}.txt"):
                        os.remove(f"{user}_saldo_{b}.txt")
                if os.path.exists(ARCHIVO_HISTORIAL):
                    os.remove(ARCHIVO_HISTORIAL)
                st.success("🗑️ ¡Historial y cuentas vaciadas con éxito!")
                st.rerun()

    # --- CONTENIDO PESTAÑA 2: INGRESOS ---
    with pest_ingreso:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("### 📈 Añadir Fondos")
        
        # Selección de banco destino
        banco_destino = st.selectbox("¿A qué banco ingresa el dinero?", ["Nequi", "Daviplata", "Nu"], key="banco_ingreso")
        monto_ingreso = st.number_input("Monto en pesos (COP):", min_value=0, step=1000, value=0, key="input_ingreso")
        detalle_ingreso = st.text_input("¿De qué es este ingreso? (Ej: Sueldo, Venta):", placeholder="Escribe el detalle aquí...", key="input_det_ingreso").strip()
        
        if st.button("Confirmar Ingreso 📈", use_container_width=True, key="btn_confirmar_ingreso"):
            if monto_ingreso > 0:
                if detalle_ingreso == "":
                    detalle_ingreso = "Ingreso general"
                
                # Cargar, sumar y guardar el nuevo saldo de ese banco específico
                saldo_actual_banco = cargar_saldo_banco(banco_destino)
                nuevo_saldo_banco = saldo_actual_banco + monto_ingreso
                guardar_saldo_banco(banco_destino, nuevo_saldo_banco)
                
                # Registrar el movimiento anotando el banco
                guardar_movimiento(f"📈 Ingreso ({banco_destino}): +${monto_ingreso:,} COP ({detalle_ingreso})")
                st.success(f"✅ ¡Se han sumado ${monto_ingreso:,} COP a tu cuenta de {banco_destino}!")
                st.rerun()
            else:
                st.warning("Por favor ingresa un valor válido.")

    # --- CONTENIDO PESTAÑA 3: GASTOS ---
    with pest_gasto:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("### 📉 Registrar un Gasto")
        
        # Selección de banco origen
        banco_origen = st.selectbox("¿De qué banco sale el dinero?", ["Nequi", "Daviplata", "Nu"], key="banco_gasto")
        monto_gasto = st.number_input("Monto en pesos (COP):", min_value=0, step=1000, value=0, key="input_gasto")
        detalle_gasto = st.text_input("¿En qué gastaste este dinero? (Ej: Almuerzo, Arriendo):", placeholder="Escribe el detalle aquí...", key="input_det_gasto").strip()
        
        if st.button("Descontar Gasto 📉", use_container_width=True, key="btn_confirmar_gasto"):
            if monto_gasto > 0:
                saldo_actual_banco = cargar_saldo_banco(banco_origen)
                
                # Validar que el banco específico tenga fondos suficientes
                if monto_gasto <= saldo_actual_banco:
                    if detalle_gasto == "":
                        detalle_gasto = "Gasto general"
                        
                    nuevo_saldo_banco = saldo_actual_banco - monto_gasto
                    guardar_saldo_banco(banco_origen, nuevo_saldo_banco)
                    
                    guardar_movimiento(f"📉 Gasto ({banco_origen}): -${monto_gasto:,} COP ({detalle_gasto})")
                    st.error(f"🛑 Gasto de ${monto_gasto:,} COP descontado de {banco_origen}.")
                    st.rerun()
                else:
                    st.warning(f"❌ Fondos insuficientes en {banco_origen}. Saldo disponible ahí: ${saldo_actual_banco:,} COP")
            else:
                st.warning("Por favor ingresa un valor válido.")
