import streamlit as st
import os

# --- ARCHIVO BASE DE DATOS DE USUARIOS ---
ARCHIVO_USUARIOS = "usuarios_db.txt"

# --- FUNCIONES PARA EL SISTEMA DE USUARIOS Y CONTRASEÑAS ---
def cargar_usuarios():
    """Carga todos los usuarios y contraseñas registrados en un diccionario"""
    usuarios = {}
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, "r") as archivo:
            for linea in archivo:
                # El archivo guarda los datos como: usuario,contraseña
                partes = linea.strip().split(",")
                if len(partes) == 2:
                    usuarios[partes[0]] = partes[1]
    return usuarios

def registrar_usuario(nuevo_usuario, nueva_contrasena):
    """Guarda un nuevo usuario y contraseña en el archivo"""
    with open(ARCHIVO_USUARIOS, "a") as archivo:
        archivo.write(f"{nuevo_usuario},{nueva_contrasena}\n")

# --- INICIALIZAR VARIABLES DE MEMORIA (SESSION STATE) ---
if 'usuario_logeado' not in st.session_state:
    st.session_state.usuario_logeado = None

# --- PANTALLA PRINCIPAL: REGISTRO / LOGIN ---
st.title("📱 Mi Control de Finanzas Pro")

# --- TRUCO PARA ESCONDER EL BOTÓN DE GITHUB Y EL MENÚ DE EDITAR ---
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    </style>
    """,
    unsafe_allow_html=True
)

if st.session_state.usuario_logeado is None:
    # Pestañas para separar el Inicio de Sesión del Registro
    pestaña_login, pestaña_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
    
    # --- PESTAÑA DE REGISTRO ---
    with pestaña_registro:
        st.subheader("Crea una cuenta nueva")
        reg_user = st.text_input("Elige un nombre de usuario:", key="reg_user").lower().strip()
        reg_pass = st.text_input("Elige una contraseña:", type="password", key="reg_pass").strip()
        
        if st.button("Crear Cuenta", key="btn_registro"):
            usuarios_existentes = cargar_usuarios()
            
            if reg_user == "" or reg_pass == "":
                st.warning("⚠️ El usuario y la contraseña no pueden estar vacíos.")
            elif reg_user in usuarios_existentes:
                st.error("❌ Este usuario ya existe. Elige otro nombre.")
            else:
                registrar_usuario(reg_user, reg_pass)
                st.success("✅ ¡Cuenta creada con éxito! Ahora puedes ir a la pestaña de 'Iniciar Sesión'.")

    # --- PESTAÑA DE INICIO DE SESIÓN ---
    with pestaña_login:
        st.subheader("Ingresa a tu cuenta")
        login_user = st.text_input("Usuario:", key="login_user").lower().strip()
        login_pass = st.text_input("Contraseña:", type="password", key="login_pass").strip()
        
        if st.button("Entrar", key="btn_login"):
            usuarios_existentes = cargar_usuarios()
            
            # Verificar si el usuario existe y la contraseña coincide
            if login_user in usuarios_existentes and usuarios_existentes[login_user] == login_pass:
                st.session_state.usuario_logeado = login_user
                st.success(f"¡Bienvenido de nuevo, {login_user.capitalize()}!")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos. Inténtalo de nuevo.")

# --- PANTALLA DE LA APLICACIÓN (CUANDO YA INICIÓ SESIÓN) ---
else:
    user = st.session_state.usuario_logeado

    # Archivos específicos para las finanzas de ESTE usuario
    ARCHIVO_SALDO = f"{user}_saldo.txt"
    ARCHIVO_HISTORIAL = f"{user}_historial.txt"

    # Funciones de finanzas personalizadas
    def cargar_saldo():
        if os.path.exists(ARCHIVO_SALDO):
            with open(ARCHIVO_SALDO, "r") as archivo:
                return int(archivo.read())
        return 0

    def guardar_saldo(nuevo_saldo):
        with open(ARCHIVO_SALDO, "w") as archivo:
            archivo.write(str(nuevo_saldo))

    def guardar_movimiento(texto):
        with open(ARCHIVO_HISTORIAL, "a") as archivo:
            archivo.write(texto + "\n")

    def cargar_historial():
        if os.path.exists(ARCHIVO_HISTORIAL):
            with open(ARCHIVO_HISTORIAL, "r") as archivo:
                return archivo.readlines()
        return []

    # Cargar el saldo en la memoria de la app
    if 'saldo' not in st.session_state:
        st.session_state.saldo = cargar_saldo()

    # --- DISEÑO VISUAL DE LA APP ---
    st.subheader(f"👤 Cuenta: {user.capitalize()}")
    
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.usuario_logeado = None
        if 'saldo' in st.session_state:
            del st.session_state.saldo
        st.rerun()
        
    st.write("---")
    st.metric(label="💰 Saldo Disponible actual", value=f"${st.session_state.saldo:,} COP")
    st.write("---")

    accion = st.radio("¿Qué deseas hacer hoy?", ["Ver Historial / Menú", "Registrar un INGRESO 📈", "Registrar un GASTO 📉"])

    # Historial
    if accion == "Ver Historial / Menú":
        st.write("### 📜 Historial de Movimientos")
        lista_movimientos = cargar_historial()
        if len(lista_movimientos) == 0:
            st.info("Aún no tienes movimientos registrados.")
        else:
            for movimiento in reversed(lista_movimientos):
                st.text(movimiento.strip())

    # Ingreso
    elif accion == "Registrar un INGRESO 📈":
        monto_ingreso = st.number_input("¿Cuánto dinero vas a ingresar?", min_value=0, step=1000)
        if st.button("Confirmar Ingreso"):
            if monto_ingreso > 0:
                st.session_state.saldo += monto_ingreso
                guardar_saldo(st.session_state.saldo)
                guardar_movimiento(f"📈 Ingreso: +${monto_ingreso:,} COP")
                st.success(f"✅ ¡Ingreso de ${monto_ingreso:,} registrado!")
                st.rerun()

    # Gasto
    elif accion == "Registrar un GASTO 📉":
        monto_gasto = st.number_input("¿De cuánto fue tu gasto?", min_value=0, step=1000)
        if st.button("Confirmar Gasto"):
            if monto_gasto > 0:
                if monto_gasto <= st.session_state.saldo:
                    st.session_state.saldo -= monto_gasto
                    guardar_saldo(st.session_state.saldo)
                    guardar_movimiento(f"📉 Gasto: -${monto_gasto:,} COP")
                    st.error(f"🛑 ¡Gasto de ${monto_gasto:,} registrado!")
                    st.rerun()
                else:
                    st.warning("❌ No tienes suficiente dinero para este gasto.")
