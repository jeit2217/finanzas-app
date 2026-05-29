import streamlit as st
import os
import smtplib
import random
from email.mime.text import MIMEText

# =====================================================================
# ⚠️ CONFIGURACIÓN DE TU CORREO REMITENTE (EL QUE ENVÍA LOS CÓDIGOS)
CORREO_REMITENTE = "jeitworld22.com"
PASSWORD_REMITENTE = "ldau cebr wdwa thst"
# =====================================================================

ARCHIVO_USUARIOS = "usuarios_db.txt"

# --- TRUCO PARA ESCONDER BOTONES DE GITHUB Y EDITAR ---
st.markdown(
    """<style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} .stAppDeployButton {display:none;}
    </style>""", unsafe_allow_html=True
)

# --- FUNCIÓN PROFESIONAL PARA ENVIAR EL CORREO ---
def enviar_correo_verificacion(correo_destino, codigo):
    try:
        msg = MIMEText(f"Hola! Tu código de verificación para Mi Control de Finanzas Pro es: {codigo}\nNo lo compartas con nadie.")
        msg['Subject'] = '🔑 Código de Verificación - Finanzas Pro'
        msg['From'] = CORREO_REMITENTE
        msg['To'] = correo_destino

        # Conexión segura con los servidores de Google Mail
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(CORREO_REMITENTE, PASSWORD_REMITENTE)
        server.sendmail(CORREO_REMITENTE, [correo_destino], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_usuarios():
    usuarios = {}
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, "r") as archivo:
            for linea in archivo:
                partes = linea.strip().split(",")
                if len(partes) == 3: # Formato: usuario,correo,contraseña
                    usuarios[partes[0]] = {"correo": partes[1], "pass": partes[2]}
    return usuarios

def registrar_usuario(usuario, correo, contrasena):
    with open(ARCHIVO_USUARIOS, "a") as archivo:
        archivo.write(f"{usuario},{correo},{contrasena}\n")

# --- INICIALIZAR VARIABLES DE MEMORIA ---
if 'usuario_logeado' not in st.session_state: st.session_state.usuario_logeado = None
if 'codigo_generado' not in st.session_state: st.session_state.codigo_generado = None
if 'datos_temporales' not in st.session_state: st.session_state.datos_temporales = None

st.title("📱 Mi Control de Finanzas Pro")

if st.session_state.usuario_logeado is None:
    pestaña_login, pestaña_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
    
    # --- PESTAÑA DE REGISTRO CON VERIFICACIÓN ---
    with pestaña_registro:
        if st.session_state.codigo_generado is None:
            st.subheader("Crea una cuenta nueva")
            reg_user = st.text_input("Nombre de usuario:", key="reg_user").lower().strip()
            reg_email = st.text_input("Tu correo de Gmail:", key="reg_email").lower().strip()
            reg_pass = st.text_input("Contraseña:", type="password", key="reg_pass").strip()
            
            if st.button("Enviar Código al Correo", key="btn_enviar_cod"):
                usuarios_existentes = cargar_usuarios()
                
                if reg_user == "" or reg_email == "" or reg_pass == "":
                    st.warning("⚠️ Todos los campos son obligatorios.")
                elif not reg_email.endswith("@gmail.com"):
                    st.error("❌ Por favor, ingresa un correo válido de Gmail (@gmail.com).")
                elif reg_user in usuarios_existentes or any(u['correo'] == reg_email for u in usuarios_existentes.values()):
                    st.error("❌ El usuario o el correo ya están registrados.")
                else:
                    # Generamos código de 6 números y lo guardamos en memoria
                    codigo = str(random.randint(100000, 999999))
                    st.session_state.codigo_generado = codigo
                    st.session_state.datos_temporales = {"user": reg_user, "email": reg_email, "pass": reg_pass}
                    
                    if enviar_correo_verificacion(reg_email, codigo):
                        st.success(f"📩 Código enviado con éxito a {reg_email}. ¡Revisa tu bandeja de entrada o spam!")
                        st.rerun()
                    else:
                        st.error("❌ Hubo un problema al enviar el correo. Revisa tus credenciales SMTP.")
                        st.session_state.codigo_generado = None
        else:
            st.subheader("🛡️ Verificación de Correo")
            st.write(f"Ingresa el código que enviamos a **{st.session_state.datos_temporales['email']}**")
            codigo_usuario = st.text_input("Código de 6 dígitos:", key="codigo_usuario").strip()
            
            if st.button("Verificar y Crear Cuenta"):
                if codigo_usuario == st.session_state.codigo_generado:
                    d = st.session_state.datos_temporales
                    registrar_usuario(d['user'], d['email'], d['pass'])
                    st.success("✅ ¡Cuenta verificada y creada con éxito! Ya puedes iniciar sesión.")
                    st.session_state.codigo_generado = None
                    st.session_state.datos_temporales = None
                    st.rerun()
                else:
                    st.error("❌ Código incorrecto. Verifica bien el número.")
            
            if st.button("❌ Cancelar Registro"):
                st.session_state.codigo_generado = None
                st.session_state.datos_temporales = None
                st.rerun()

    # --- PESTAÑA DE INICIO DE SESIÓN (CORREO O USUARIO) ---
    with pestaña_login:
        st.subheader("Ingresa a tu cuenta")
        login_input = st.text_input("Usuario o Correo de Gmail:", key="login_input").lower().strip()
        login_pass = st.text_input("Contraseña:", type="password", key="login_pass").strip()
        
        if st.button("Entrar", key="btn_login"):
            usuarios_existentes = cargar_usuarios()
            usuario_encontrado = None
            
            # Buscamos si coincide con un nombre de usuario directo o con el correo de algún usuario
            if login_input in usuarios_existentes:
                usuario_encontrado = login_input
            else:
                for u, datos in usuarios_existentes.items():
                    if datos["correo"] == login_input:
                        usuario_encontrado = u
                        break
            
            if usuario_encontrado and usuarios_existentes[usuario_encontrado]["pass"] == login_pass:
                st.session_state.usuario_logeado = usuario_encontrado
                st.success(f"¡Bienvenido de nuevo, {usuario_encontrado.capitalize()}!")
                st.rerun()
            else:
                st.error("❌ Los datos de acceso no coinciden. Inténtalo de nuevo.")

# --- PANTALLA PRIVADA DEL USUARIO ---
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

    if 'saldo' not in st.session_state: st.session_state.saldo = cargar_saldo()

    st.subheader(f"👤 Cuenta: {user.capitalize()}")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.usuario_logeado = None
        if 'saldo' in st.session_state: del st.session_state.saldo
        st.rerun()
        
    st.write("---")
    st.metric(label="💰 Saldo Disponible actual", value=f"${st.session_state.saldo:,} COP")
    st.write("---")

    accion = st.radio("¿Qué deseas hacer hoy?", ["Ver Historial / Menú", "Registrar un INGRESO 📈", "Registrar un GASTO 📉"])

    if accion == "Ver Historial / Menú":
        st.write("### 📜 Historial de Movimientos")
        lista_movimientos = cargar_historial()
        if len(lista_movimientos) == 0: st.info("Aún no tienes movimientos registrados.")
        else:
            for movimiento in reversed(lista_movimientos): st.text(movimiento.strip())

    elif accion == "Registrar un INGRESO 📈":
        monto_ingreso = st.number_input("¿Cuánto dinero vas a ingresar?", min_value=0, step=1000)
        if st.button("Confirmar Ingreso"):
            if monto_ingreso > 0:
                st.session_state.saldo += monto_ingreso
                guardar_saldo(st.session_state.saldo)
                guardar_movimiento(f"📈 Ingreso: +${monto_ingreso:,} COP")
                st.success(f"✅ ¡Ingreso de ${monto_ingreso:,} registrado!")
                st.rerun()

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
                    st.warning("❌ No tienes suficiente dinero.")
