import streamlit as st
import os
import json
from datetime import datetime
import uuid

# ConfiguraciÃ³n de la pÃ¡gina
st.set_page_config(
    page_title="Sistema de Monitoreo de Sensores",
    page_icon="ðŸ“Š",
    layout="wide"
)

# Rutas de archivos
DB_FILE = "db.json"
USER_DB_FILE = "users.json"

# InicializaciÃ³n de la base de datos
def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"sensors": []}, f)
    
    if not os.path.exists(USER_DB_FILE):
        default_admin = {
            "username": "admin",
            "password": "admin123",
            "role": "admin"
        }
        with open(USER_DB_FILE, "w") as f:
            json.dump({"users": [default_admin]}, f)

# Operaciones CRUD para sensores
def get_sensors():
    with open(DB_FILE, "r") as f:
        data = json.load(f)
    return data.get("sensors", [])

def add_sensor(name, type, location, value):
    sensors = get_sensors()
    new_sensor = {
        "id": str(uuid.uuid4()),
        "name": name,
        "type": type,
        "location": location,
        "value": value,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    sensors.append(new_sensor)
    with open(DB_FILE, "w") as f:
        json.dump({"sensors": sensors}, f)
    return new_sensor

def delete_sensor(sensor_id):
    sensors = get_sensors()
    updated_sensors = [s for s in sensors if s["id"] != sensor_id]
    with open(DB_FILE, "w") as f:
        json.dump({"sensors": updated_sensors}, f)

# Operaciones de usuarios
def get_users():
    with open(USER_DB_FILE, "r") as f:
        data = json.load(f)
    return data.get("users", [])

def add_user(username, password, role="user"):
    users = get_users()
    if any(user["username"] == username for user in users):
        return False
    new_user = {
        "username": username,
        "password": password,
        "role": role
    }
    users.append(new_user)
    with open(USER_DB_FILE, "w") as f:
        json.dump({"users": users}, f)
    return True

def authenticate(username, password):
    users = get_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return user
    return None

# Inicializar la base de datos
init_db()

# Inicializar el estado de la sesiÃ³n
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "user" not in st.session_state:
    st.session_state.user = None
if "show_registration" not in st.session_state:
    st.session_state.show_registration = False

# Funciones de navegaciÃ³n
def go_to_login():
    st.session_state.page = "login"
    st.session_state.show_registration = False

def go_to_landing():
    st.session_state.page = "landing"

def go_to_dashboard():
    st.session_state.page = "dashboard"

def logout():
    st.session_state.user = None
    st.session_state.page = "landing"

def show_register_form():
    st.session_state.show_registration = True

def show_login_form():
    st.session_state.show_registration = False

# PÃ¡gina de inicio (Landing)
def landing_page():
    st.title("Sistema de Monitoreo de Sensores")
    
    st.markdown("""
    ## Bienvenido a nuestra plataforma de monitoreo
    
    Esta aplicaciÃ³n proporciona una soluciÃ³n completa para monitorizar y gestionar sus sensores.
    
    ### CaracterÃ­sticas principales:
    
    - ðŸ“Š VisualizaciÃ³n en tiempo real
    - ðŸ” Sistema de autenticaciÃ³n seguro
    - ðŸ‘¥ Diferentes roles de usuario
    - ðŸ“± Interfaz responsiva y moderna
    
    ### Acerca del proyecto
    
    Este sistema permite monitorear sensores diversos como temperatura, humedad, 
    presiÃ³n y mÃ¡s. Los administradores pueden agregar, eliminar y gestionar sensores,
    mientras que los usuarios pueden visualizar las lecturas actuales.
    """)
    
    # Imagen placeholder para la landing page
    st.image("https://via.placeholder.com/800x400?text=Sistema+de+Monitoreo+de+Sensores", 
             caption="Plataforma de monitoreo avanzada")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.button("Iniciar SesiÃ³n", use_container_width=True, on_click=go_to_login)

# PÃ¡gina de login/registro
def login_page():
    st.title("Acceso al Sistema")
    
    tab1, tab2 = st.tabs(["Iniciar SesiÃ³n", "Registrarse"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("ContraseÃ±a", type="password")
            submit = st.form_submit_button("Ingresar")
            
            if submit:
                user = authenticate(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("Usuario o contraseÃ±a incorrectos")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Nuevo Usuario")
            new_password = st.text_input("Nueva ContraseÃ±a", type="password")
            confirm_password = st.text_input("Confirmar ContraseÃ±a", type="password")
            submit_reg = st.form_submit_button("Registrarse")
            
            if submit_reg:
                if new_password != confirm_password:
                    st.error("Las contraseÃ±as no coinciden")
                elif len(new_username) < 3:
                    st.error("El nombre de usuario debe tener al menos 3 caracteres")
                elif len(new_password) < 6:
                    st.error("La contraseÃ±a debe tener al menos 6 caracteres")
                else:
                    success = add_user(new_username, new_password)
                    if success:
                        st.success("Usuario registrado correctamente. Ahora puede iniciar sesiÃ³n.")
                        show_login_form()
                    else:
                        st.error("El nombre de usuario ya existe")
    
    with st.container():
        st.button("Volver a la pÃ¡gina principal", on_click=go_to_landing)

# PÃ¡gina de dashboard
def dashboard_page():
    # Verificar si el usuario estÃ¡ autenticado
    if not st.session_state.user:
        st.warning("Debe iniciar sesiÃ³n para acceder a esta pÃ¡gina")
        st.button("Ir a Login", on_click=go_to_login)
        return
    
    st.title(f"Dashboard - Bienvenido, {st.session_state.user['username']}")
    
    # Mostrar menÃº lateral
    with st.sidebar:
        st.title("MenÃº")
        st.text(f"Usuario: {st.session_state.user['username']}")
        st.text(f"Rol: {st.session_state.user['role']}")
        st.divider()
        st.button("Ver Sensores", use_container_width=True, key="btn_view_sensors")
        
        # Solo mostrar opciones de administrador si el usuario tiene ese rol
        if st.session_state.user["role"] == "admin":
            st.button("Administrar Sensores", use_container_width=True, key="btn_manage_sensors")
        
        st.button("Cerrar SesiÃ³n", use_container_width=True, on_click=logout)
    
    # Contenido principal
    tab1, tab2 = st.tabs(["Ver Sensores", "Administrar Sensores" if st.session_state.user["role"] == "admin" else ""])
    
    # PestaÃ±a de visualizaciÃ³n de sensores (para todos los usuarios)
    with tab1:
        st.header("Sensores Activos")
        sensors = get_sensors()
        
        if not sensors:
            st.info("No hay sensores registrados actualmente.")
        else:
            # Crear una cuadrÃ­cula para mostrar sensores
            cols = st.columns(3)
            for i, sensor in enumerate(sensors):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.subheader(sensor["name"])
                        st.metric("Valor", sensor["value"])
                        st.caption(f"Tipo: {sensor['type']}")
                        st.caption(f"UbicaciÃ³n: {sensor['location']}")
                        st.caption(f"Ãšltima actualizaciÃ³n: {sensor['timestamp']}")
    
    # PestaÃ±a de administraciÃ³n (solo para administradores)
    if st.session_state.user["role"] == "admin":
        with tab2:
            st.header("Administrar Sensores")
            
            # Formulario para agregar un nuevo sensor
            with st.expander("Agregar nuevo sensor", expanded=True):
                with st.form("add_sensor_form"):
                    name = st.text_input("Nombre del sensor")
                    col1, col2 = st.columns(2)
                    with col1:
                        sensor_type = st.selectbox("Tipo", ["Temperatura", "Humedad", "PresiÃ³n", "Luz", "Movimiento", "Otro"])
                    with col2:
                        location = st.text_input("UbicaciÃ³n")
                    value = st.slider("Valor inicial", 0, 100, 50)
                    
                    submit = st.form_submit_button("Agregar Sensor")
                    if submit:
                        if name and location:
                            new_sensor = add_sensor(name, sensor_type, location, value)
                            st.success(f"Sensor '{name}' agregado correctamente")
                        else:
                            st.error("Por favor complete todos los campos")
            
            # Lista de sensores con opciÃ³n de eliminar
            st.subheader("Sensores Existentes")
            sensors = get_sensors()
            
            if not sensors:
                st.info("No hay sensores registrados.")
            else:
                for sensor in sensors:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{sensor['name']}** - {sensor['type']} ({sensor['location']})")
                    with col2:
                        if st.button("Eliminar", key=f"del_{sensor['id']}"):
                            delete_sensor(sensor['id'])
                            st.success(f"Sensor '{sensor['name']}' eliminado")
                            st.rerun()

# Routing principal
if st.session_state.page == "landing":
    landing_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "dashboard":
    dashboard_page()
