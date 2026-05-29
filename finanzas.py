import streamlit as st
import os

# --- ARCHIVO BASE DE DATOS DE USUARIOS ---
ARCHIVO_USUARIOS = "usuarios_db.txt"

# --- TRUCO PARA ESCONDER BOTONES DE GITHUB Y EDITAR ---
st.markdown(
    """<style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} .stAppDeployButton {display:none;}
    </style>""", unsafe_allow_html=True
)

# --- FUNCIONES PARA EL SISTEMA DE USUARIOS Y CONTRASEÑAS ---
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

# --- INICIALIZAR VARIABLES DE MEMORIA (SESSION STATE) ---
if 'usuario_logeado' not in st.session_state:
    st.session_state.usuario_logeado = None

# --- PANTALLA PRINCIPAL ---
st.title("📱 Mi Control de Finanzas Pro")

if st.session_state.usuario_logeado is None:
    pestaña_login, pestaña_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
    
    # --- PESTAÑA DE REGISTRO ---
    with pestaña_registro:
        st.subheader("Crea una cuenta nueva")
        reg_user = st.text_input("Elige tu nombre de usuario:", key="reg_user").lower().strip()
        reg_pass = st.text_input("Elige tu contraseña:", type="password", key="reg_pass").strip()
        
        if st.button("Crear Cuenta", key="btn_registro"):
            usuarios_existentes = cargar_usuarios()
            
            if reg_user == "" or reg_pass == "":
                st.warning("⚠️ El usuario y la contraseña no pueden estar vacíos.")
            elif reg_user in usuarios_existentes:
                st.error("❌ Este usuario ya existe. Elige otro nombre.")
            else:
                registrar_usuario(reg_user, reg_pass)
                st.success("✅ ¡Cuenta creada con éxito! Ya puedes ir a la pestaña de 'Iniciar Sesión'.")

    # --- PESTAÑA DE INICIO DE SESIÓN ---
    with pestaña_login:
        st.subheader("Ingresa a tu cuenta")
        login_user = st.text_input("Usuario:", key="login_user").lower().strip()
        login_pass = st.text_input("Contraseña:", type="password", key="login_pass").strip()
        
        if st.button("Entrar", key="btn_login"):
            usuarios_existentes = cargar_usuarios()
            
            if login_user in usuarios_existentes and usuarios_existentes[login_user] == login_pass:
                st.session_state.usuario_logeado = login_user
                st.success(f"¡Bienvenido de nuevo, {login_user.capitalize()}!")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos. Inténtalo de nuevo.")

# --- PANTALLA DE LA APLICACIÓN (CUANDO YA INICIÓ SESIÓN) ---
else:
    user = st.session_state.usuario_logeado

    # Archivos específicos para cada usuario independiente
    ARCHIVO_SALDO = f"{user}_saldo.txt"
    ARCHIVO_HISTORIAL = f"{
