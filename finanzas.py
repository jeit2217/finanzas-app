%%writefile app.py
import streamlit as st
import os

# --- CONTROL DE INICIO DE SESIÓN ---
st.title("📱 Mi Control de Finanzas Multi-Usuario")

# Creamos una variable en la memoria de la app para saber si ya iniciaron sesión
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

# Si nadie ha iniciado sesión, mostramos la pantalla de bienvenida
if st.session_state.usuario is None:
    st.subheader("Por favor, inicia sesión para continuar")
    
    # Caja de texto para escribir el nombre de usuario
    nombre = st.text_input("Ingresa tu nombre de usuario (en minúsculas y sin espacios):").lower().strip()
    
    if st.button("Entrar a mi cuenta"):
        if nombre != "":
            st.session_state.usuario = nombre
            st.success(f"¡Bienvenido, {nombre.capitalize()}!")
            st.rerun()
        else:
            st.warning("Por favor, escribe un nombre válido.")

# Si ya hay un usuario logueado, cargamos SU aplicación privada
else:
    user = st.session_state.usuario

    # Nombres de archivos personalizados para cada usuario
    ARCHIVO_SALDO = f"{user}_saldo.txt"
    ARCHIVO_HISTORIAL = f"{user}_historial.txt"

    # --- FUNCIONES DE ARCHIVOS ---
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

    # Cargar saldo inicial del usuario actual
    if 'saldo' not in st.session_state:
        st.session_state.saldo = cargar_saldo()

    # --- DISEÑO DE LA APP PRIVADA ---
    st.subheader(f"Cuenta de: {user.capitalize()}")
    
    # Botón para cerrar sesión arriba a la derecha
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.usuario = None
        # Limpiamos el saldo de la memoria para que el siguiente no lo vea
        if 'saldo' in st.session_state:
            del st.session_state.saldo
        st.rerun()
        
    st.write("---")
    st.metric(label="💰 Saldo Disponible actual", value=f"${st.session_state.saldo:,} COP")
    st.write("---")

    accion = st.radio("¿Qué deseas hacer hoy?", ["Ver Historial / Menú", "Registrar un INGRESO 📈", "Registrar un GASTO 📉"])

    # Historial privado
    if accion == "Ver Historial / Menú":
        st.write("### 📜 Historial de Movimientos")
        lista_movimientos = cargar_historial()
        if len(lista_movimientos) == 0:
            st.info("Aún no tienes movimientos registrados.")
        else:
            for movimiento in reversed(lista_movimientos):
                st.text(movimiento.strip())

    # Ingreso privado
    elif accion == "Registrar un INGRESO 📈":
        monto_ingreso = st.number_input("¿Cuánto dinero vas a ingresar?", min_value=0, step=1000)
        if st.button("Confirmar Ingreso"):
            if monto_ingreso > 0:
                st.session_state.saldo += monto_ingreso
                guardar_saldo(st.session_state.saldo)
                guardar_movimiento(f"📈 Ingreso: +${monto_ingreso:,} COP")
                st.success(f"✅ ¡Ingreso de ${monto_ingreso:,} registrado!")
                st.rerun()

    # Gasto privado
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