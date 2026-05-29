import streamlit as st
import os

# --- ARCHIVO BASE DE DATOS DE USUARIOS ---
ARCHIVO_USUARIOS = "usuarios_db.txt"

# --- CONFIGURACIÓN DE LA PÁGINA Y DISEÑO PREMIUM ---
st.set_page_config(page_title="Finanzas Pro", page_icon="💰", layout="centered")

# Truco CSS avanzado para cambiar fondos, esconder botones de GitHub y mejorar la estética
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} .stAppDeployButton {display:none;}
    
    /* Fondo general de la app y tipografía */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Estilo para la tarjeta del Saldo */
    .tarjeta-saldo {
        background: linear-gradient(135deg, #1d3557 0%, #457b9d 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 25px;
    }
    .tarjeta-saldo h3 {
        margin: 0;
        font-size: 1.1rem;
        opacity: 0.9;
        color: #e63946 !important; /* Detalle de color elegante */
    }
    .tarjeta-saldo h1 {
        margin: 5px 0 0 0;
        font-size: 2.3rem;
        font-weight: 700;
    }
    
    /* Estilo para los bloques del historial */
    .item-historial {
        background-color: white;
        padding: 12px 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        border-left: 5px solid #ccc;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }
    .ingreso-style { border-left-color: #2a9d8f; }
    .gasto-style { border-left-color: #e63946; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- FUNCIONES DE USUARIOS ---
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

# --- INICIALIZAR VARIABLES ---
if 'usuario_logeado' not in st.session_state:
    st.session_state.usuario_logeado = None

# --- PANTALLA DE ACCESO (LOGIN / REGISTRO) ---
if st.session_state.usuario_logeado is None:
    st.markdown("<h1 style='text-align: center; color: #1d3557;'>📱 Control de Finanzas Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6c757d;'>Gestiona tus ingresos y gastos de forma privada y organizada.</p>", unsafe_allow_html=True)
    
    # Caja contenedora visual para el login
    with st.container():
        pestaña_login, pestaña_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
        
        with pestaña_registro:
            st.write("### Crea tu cuenta")
            reg_user = st.text_input("Elige tu nombre de usuario:", key="reg_user").lower().strip()
            reg_pass = st.text_input("Elige tu contraseña:", type="password", key="reg_pass").strip()
            
            if st.button("Crear Cuenta ✨", key="btn_registro", use_container_width=True):
                usuarios_existentes = cargar_usuarios()
                if reg_user == "" or reg_pass == "":
                    st.warning("⚠️ El usuario y la contraseña no pueden estar vacíos.")
                elif reg_user in usuarios_existentes:
                    st.error("❌ Este usuario ya existe. Elige otro nombre.")
                else:
                    registrar_usuario(reg_user, reg_pass)
                    st.success("✅ ¡Cuenta creada con éxito! Pasa a la pestaña de 'Iniciar Sesión'.")

        with pestaña_login:
            st.write("### Ingresa a tu panel")
            login_user = st.text_input("Usuario:", key="login_user").lower().strip()
            login_pass = st.text_input("Contraseña:", type="password", key="login_pass").strip()
            
            if st.button("Entrar Seguro 🚀", key="btn_login", use_container_width=True):
                usuarios_existentes = cargar_usuarios()
                if login_user in usuarios_existentes and usuarios_existentes[login_user] == login_pass:
                    st.session_state.usuario_logeado = login_user
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")

# --- PANTALLA PRINCIPAL CON DISEÑO PREMIUM ---
else:
    user = st.session_state.usuario_logeado

    ARCHIVO_SALDO = f"{user}_saldo.txt"
    ARCHIVO_HISTORIAL = f"{user}_historial.txt"

    def cargar_saldo():
        if os.path.exists(ARCHIVO_SALDO):
            with open(ARCHIVO_SALDO, "r") as archivo: return int(archivo.read())
        return 0
    def guardar_saldo(nuevo_saldo):
        with open(ARCHIVO_SALDO, "w") as archivo: archivo.write(str(nuevo_saldo))
    def guardar_movimiento(texto):
        with open(ARCHIVO_HISTORIAL, "a") as archivo: archivo.write(texto + "\n")
    def cargar_historial():
        if os.path.exists(ARCHIVO_HISTORIAL):
            with open(ARCHIVO_HISTORIAL, "r") as archivo: return archivo.readlines()
        return []

    if 'saldo' not in st.session_state:
        st.session_state.saldo = cargar_saldo()

    # --- MENÚ LATERAL (SIDEBAR) REORGANIZADO ---
    with st.sidebar:
        st.markdown(f"### 👤 Bienvenido,<br><h2 style='color:#1d3557; margin-top:0;'>{user.capitalize()}</h2>", unsafe_allow_html=True)
        st.write("---")
        
        # El menú de navegación ahora está guardado elegantemente a la izquierda
        st.markdown("#### 🎯 Menú de Navegación")
        accion = st.radio(
            "Selecciona una opción:", 
            ["📊 Ver Mi Panel y Historial", "📈 Registrar Ingreso", "📉 Registrar Gasto"]
        )
        
        st.write("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_logeado = None
            if 'saldo' in st.session_state: del st.session_state
