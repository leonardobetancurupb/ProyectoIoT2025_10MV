import streamlit as st
import pandas as pd
import numpy as np
import os
import json

# Configuración de la página
st.set_page_config(page_title="Dashboard de Sensores", page_icon="📊", layout="wide")

# Simulación de base de datos de usuarios (en un archivo de texto plano)
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {"admin": {"password": "admin", "role": "admin"}}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# Función para mostrar la página de inicio
def show_home():
    st.title("Proyecto IoT: Dashboard de Sensores")
    st.write("""
    Bienvenido al proyecto IoT de monitoreo de sensores de humedad.
    Este sistema centraliza los datos de los sensores y ofrece un dashboard interactivo.
    """)
    if st.button("Ir al Login"):
        st.session_state.page = "login"

# Función para el registro de usuarios
def register():
    st.title("Registro de Usuario")
    new_username = st.text_input("Nuevo Usuario")
    new_password = st.text_input("Nueva Contraseña", type="password")
    if st.button("Registrarse"):
        users = load_users()
        if new_username in users:
            st.error("El usuario ya existe.")
        else:
            users[new_username] = {"password": new_password, "role": "user"}
            save_users(users)
            st.success("Registro exitoso. Ahora puedes iniciar sesión.")
            st.session_state.page = "login"

# Función para el login
def login():
    st.title("Login")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
        users = load_users()
        if username in users and users[username]["password"] == password:
            st.session_state.user = username
            st.session_state.role = users[username]["role"]
            st.success("Login exitoso!")
            st.session_state.page = "dashboard"
        else:
            st.error("Usuario o contraseña incorrectos")
    if st.button("Registrarse"):
        st.session_state.page = "register"

# Función para cargar datos de sensores (simulados)
def load_sensor_data():
    data = {
        "Sensor 1": np.random.normal(70, 10, 100),
        "Sensor 2": np.random.normal(65, 8, 100),
        "Sensor 3": np.random.normal(75, 12, 100)
    }
    return pd.DataFrame(data)

# Función para mostrar el dashboard
def show_dashboard():
    st.title("Dashboard de Sensores")
    st.write(f"Bienvenido, {st.session_state.user} (Rol: {st.session_state.role})")

    # Cargar datos
    df = load_sensor_data()

    # Mostrar gráficos
    st.subheader("Datos de Sensores")
    st.line_chart(df)

    # Mostrar estadísticas
    st.subheader("Estadísticas")
    st.write(df.describe())

    # Funcionalidades según el rol
    if st.session_state.role == "admin":
        st.subheader("Panel de Administrador")
        if st.button("Eliminar Datos"):
            st.warning("Funcionalidad de eliminación simulada.")
        if st.button("Agregar Datos"):
            st.warning("Funcionalidad de agregar datos simulada.")
    else:
        st.write("Rol de Usuario: Solo visualización permitida.")

# Main
if __name__ == "__main__":
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if st.session_state.page == "home":
        show_home()
    elif st.session_state.page == "login":
        login()
    elif st.session_state.page == "register":
        register()
    elif st.session_state.page == "dashboard":
        show_dashboard() 