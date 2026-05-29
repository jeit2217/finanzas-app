import streamlit as st
import os

# --- ARCHIVO BASE DE DATOS DE USUARIOS ---
ARCHIVO_USUARIOS = "usuarios_db.txt"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Finanzas Pro", page_icon="💰", layout="centered")

# --- MENÚ LATERAL (SIDEBAR) - CONTROL DE SESIÓN Y TEMA ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>🎨 Apariencia</h2>", unsafe_allow_html=True)
    tema = st.radio("Elige el estilo visual:", ["Modo Claro ☀️", "Modo Oscuro 🌙"], label_visibility="collapsed")
    st.write("---")

# --- DISEÑO VISUAL ADAPTATIVO (ESTILOS BASE EN TEXTO LIMPIO) ---
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} .stAppDeployButton {display:none;}
    
    .tarjeta-saldo {
        color: white !important;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0px 10px 25px rgba(0, 0, 0, 0.15);
        text-align: center;
        margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .tarjeta-saldo h3 {
        margin: 0 !important;
        font-size: 0.95rem !important;
        letter-spacing: 1.5px;
        opacity: 0.85;
        color: #f1faee !important;
    }
    .tarjeta-saldo h1 {
        margin: 10px 0 0 0 !important;
        font-size: 2.6rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    
    .item-historial {
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 6px solid #ccc;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.02);
        font-family: monospace;
        font-size: 0.95rem;
    }
    .ingreso-style { border-left-color: #2a9d8f !important; }
    .gasto-style { border-left-color: #e63946 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- INYECCIÓN DE COLORES SEGÚN EL TEMA SELECCIONADO ---
if tema == "Modo Oscuro 🌙":
    st.markdown(
        """
        <style>
        .stApp { background-color: #121212 !important; color: #e0e0e0 !important; }
        h1, h2, h3, h4, p, label, .stMarkdown { color: #e0e0e0 !important; }
        .tarjeta-saldo { background: linear-gradient(135deg, #1f4068 0%, #162447 100%); }
        .item-historial { background-color: #1b1b1b; color: #e0e0e0; border: 1px solid #333; }
        </style>
        """, unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        .stApp { background-color: #f8f9fa !important; color: #212529 !important; }
        h1, h2, h3, h4, p, label, .stMarkdown { color: #212529 !important; }
        .tarjeta-saldo { background: linear-gradient(135deg, #1d3557 0%, #457b9d 100%); }
        .item-historial { background-color: #ffffff; color: #212529; border: 1px solid #e9ecef; }
        </style>
        """, unsafe_allow_html=True
    )

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

    # Archivos independientes por usuario
    ARCHIVO_SALDO = f"{user}_saldo.txt"
    ARCHIVO_HISTORIAL = f"{user}_historial.txt"

    def cargar_saldo():
        if os.path.exists(ARCHIVO_SALDO):
            with open(ARCHIVO_

