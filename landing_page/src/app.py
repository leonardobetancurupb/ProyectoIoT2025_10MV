import streamlit as st
import os
import json
from datetime import datetime
import uuid
import requests
from requests.auth import HTTPBasicAuth

st.set_page_config(
    page_title="Sistema de Monitoreo de Sensores",
    page_icon="📊",
    layout="wide"
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
USER_DB_FILE = os.path.join(DATA_DIR, "users.json")

ORION_EXTERNAL_HOST = "10.38.32.137"
ORION_EXTERNAL_PORT = "5026"
ORION_API_VERSION_PATH = "/v2"
ORION_BASE_URL = f"http://{ORION_EXTERNAL_HOST}:{ORION_EXTERNAL_PORT}{ORION_API_VERSION_PATH}"
ORION_API_USER = "admin"
ORION_API_PASSWORD = "adminpass"
NGSI_HEADERS = {'Content-Type': 'application/json'}
ORION_AUTH = HTTPBasicAuth(ORION_API_USER, ORION_API_PASSWORD)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "page" not in st.session_state:
    st.session_state.page = "Home"

def init_user_db():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(USER_DB_FILE):
        default_admin = {"username": "admin", "password": "admin123", "role": "admin"}
        with open(USER_DB_FILE, "w") as f:
            json.dump({"users": [default_admin]}, f)

def orion_request(method, endpoint, json_data=None, params=None):
    url = f"{ORION_BASE_URL}{endpoint}"
    current_headers = NGSI_HEADERS.copy()
    if method.upper() in ["GET", "DELETE"]:
        if 'Content-Type' in current_headers:
            del current_headers['Content-Type']
    request_kwargs = {"auth": ORION_AUTH, "params": params, "headers": current_headers}
    if method.upper() not in ["GET", "DELETE"] and json_data is not None:
        request_kwargs["json"] = json_data
    try:
        response = requests.request(method, url, **request_kwargs)
        response.raise_for_status()
        if response.status_code == 204: return True
        return response.json() if response.content else True
    except requests.exceptions.HTTPError as e:
        error_details = e.response.text
        try: error_details = e.response.json()
        except ValueError: pass
        st.error(f"Error de API Orion (HTTP): {e.response.status_code} - Detalles: {error_details}")
    except requests.exceptions.ConnectionError:
        st.error(f"Error de Conexión: No se pudo conectar a Orion en {url}.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error de Request General: {e}")
    return None

def get_entities_from_orion():
    entities = orion_request("GET", "/entities")
    return entities if isinstance(entities, list) else []

def add_entity_to_orion(entity_data):
    response = orion_request("POST", "/entities", json_data=entity_data)
    return response is not None

def create_sensor_entity_payload(name, sensor_type_attr, location, value):
    sensor_id = f"Sensor:{uuid.uuid4()}"
    return {
        "id": sensor_id, "type": "Sensor",
        "name": {"type": "Text", "value": name},
        "sensorType": {"type": "Text", "value": sensor_type_attr},
        "location": {"type": "Text", "value": location},
        "currentValue": {"type": "Number", "value": float(value)},
        "timestamp": {"type": "DateTime", "value": datetime.utcnow().isoformat() + "Z"}
    }

def delete_entity_from_orion(entity_id):
    return orion_request("DELETE", f"/entities/{entity_id}") is True

def get_users():
    if not os.path.exists(USER_DB_FILE): return []
    with open(USER_DB_FILE, "r") as f: data = json.load(f)
    return data.get("users", [])

def add_user_to_db(username, password, role="user"):
    users = get_users()
    if any(user["username"] == username for user in users):
        st.error("El nombre de usuario ya existe.")
        return False
    new_user = {"username": username, "password": password, "role": role}
    users.append(new_user)
    with open(USER_DB_FILE, "w") as f: json.dump({"users": users}, f)
    st.success("Usuario registrado correctamente. Ahora puede iniciar sesión.")
    return True

def authenticate_user(username, password):
    users = get_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return user
    st.error("Usuario o contraseña incorrectos.")
    return None

init_user_db()

def go_to_page(page_name):
    st.session_state.page = page_name
    st.rerun()

def logout_user():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.page = "Home"
    st.rerun()

st.sidebar.title("Navegación")
if st.sidebar.button("Home", key="nav_home", use_container_width=True):
    go_to_page("Home")
if st.sidebar.button("About", key="nav_about", use_container_width=True):
    go_to_page("About")
if st.session_state.logged_in:
    if st.sidebar.button("Dashboard", key="nav_dashboard", use_container_width=True):
        go_to_page("Dashboard")
    if st.session_state.current_user and st.session_state.current_user.get("role") == "admin":
        if st.sidebar.button("Manage Sensors (CRUD)", key="nav_crud", use_container_width=True):
            go_to_page("Manage Sensors")
    if st.sidebar.button("Cerrar sesión", key="nav_logout", use_container_width=True):
        logout_user()
    if st.session_state.current_user:
         st.sidebar.markdown(f"**Usuario:** {st.session_state.current_user['username']} ({st.session_state.current_user['role']})")
else:
    if st.sidebar.button("Login", key="nav_login", use_container_width=True):
        go_to_page("Login")
    if st.sidebar.button("Registro", key="nav_register", use_container_width=True):
        go_to_page("Registro")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "../assets/images")
# Cambia la imagen del sidebar a una local
st.sidebar.image(os.path.join(ASSETS_DIR, "banner.png"), use_container_width=True)

if st.session_state.page == "Home":
    st.title("Sistema de Monitoreo de Sensores IoT")
  
    # col1, col2, col3 = st.columns([1, 2, 1])
    # with col2:
    #     st.image(os.path.join(ASSETS_DIR, "banner.png"), width=600)
    st.markdown("""
    ## ¡Bienvenido a nuestra plataforma de monitoreo!
    Esta aplicación proporciona una solución completa para monitorizar y gestionar sus sensores.
    Utiliza FIWARE Orion para la gestión de datos de contexto en tiempo real.
    
    ### Características principales
    - Monitoreo en tiempo real de sensores IoT.
    - Visualización de datos históricos y actuales.
    - Gestión de usuarios y roles (admin/usuario).
    - Integración con FIWARE Orion Context Broker y CrateDB.
    - Panel de control interactivo y fácil de usar.
    
    ### Beneficios de la plataforma
    1. **Escalabilidad:** Permite agregar nuevos sensores y entidades fácilmente.
    2. **Interactividad:** Interfaz intuitiva basada en Streamlit para una experiencia de usuario fluida.
    3. **Seguridad:** Control de acceso mediante autenticación y roles.
    4. **Flexibilidad:** Adaptable a diferentes tipos de sensores y casos de uso.
    5. **Despliegue sencillo:** Uso de Docker y Docker Compose para facilitar la instalación y ejecución.
    
    ### Tecnologías utilizadas
    - **Streamlit:** Para la creación de la interfaz web.
    - **FIWARE Orion Context Broker:** Para la gestión de datos de contexto.
    - **CrateDB:** Almacenamiento de datos históricos.
    - **Grafana:** Visualización avanzada de datos.
    - **Docker:** Contenerización y despliegue.
    
    ### ¿Cómo empezar?
    1. Regístrate o inicia sesión en la plataforma.
    2. Agrega y gestiona tus sensores desde el panel de administración.
    3. Visualiza los datos en tiempo real y genera reportes.
    4. Personaliza la plataforma según tus necesidades.
    """)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(os.path.join(ASSETS_DIR, "FIWARE-Orion-LD-Context-Broker.png"), width=600)
    
    
    if not st.session_state.logged_in:
        if st.button("Iniciar Sesión para ver más", use_container_width=True):
            go_to_page("Login")

elif st.session_state.page == "About":
    st.title("Acerca de Nosotros y el Sistema")
    st.subheader("Autores del Proyecto")
    authors = [
        {"name": "Camilo Andrés", "image": os.path.join(ASSETS_DIR, "CamiloAndres.png"), "description": "Me gustan los animales, especialmente los gatos y la tecnología"},
        {"name": "Andrés Sanchez", "image": os.path.join(ASSETS_DIR, "AndresSanchez.jpeg"), "description": "Amante de la naturaleza y la tecnología"},
        {"name": "David Romero", "image": os.path.join(ASSETS_DIR, "DavidRomero.png"), "description": "Apasionado por la inteligencia artificial"},
        {"name": "Alejandro Gomez", "image": os.path.join(ASSETS_DIR, "AlejandroGomez.png"), "description": "Amante de la tecnología y la ciencia"}
    ]
    cols = st.columns(len(authors))
    for col, author in zip(cols, authors):
        with col:
            st.image(author["image"], width=100)
            st.markdown(f"**{author['name']}**")
            st.markdown(author["description"])

    st.subheader("Descripción del Sistema")
    st.markdown("""
    Este sistema de monitoreo de sensores IoT ha sido desarrollado para demostrar la integración
    de Streamlit como front-end con un backend FIWARE.

    **Tecnologías Clave:**
    - Streamlit: Framework de Python para crear aplicaciones web interactivas de manera rápida y sencilla.
    - FIWARE Orion Context Broker: Permite la gestión de datos de contexto en tiempo real, facilitando la integración de sensores IoT.
    - Docker & Docker Compose: Herramientas para la contenerización y despliegue eficiente de aplicaciones.
    - Python: Lenguaje de programación utilizado para desarrollar la lógica del sistema.
    - Requests: Biblioteca de Python para realizar solicitudes HTTP y comunicarse con el broker Orion.
    - JSON: Formato de datos utilizado para la comunicación entre el front-end y el backend.
    """)

elif st.session_state.page == "Login":
    st.title("Iniciar Sesión")
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit_login = st.form_submit_button("Ingresar")
        if submit_login:
            user = authenticate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.success(f"Bienvenido, {user['username']}!")
                go_to_page("Dashboard")

elif st.session_state.page == "Registro":
    st.title("Registro de Usuario")
    with st.form("register_form"):
        new_username = st.text_input("Nuevo Usuario")
        new_password = st.text_input("Nueva Contraseña", type="password")
        confirm_password = st.text_input("Confirmar Contraseña", type="password")
        submit_reg = st.form_submit_button("Registrarse")
        if submit_reg:
            if not new_username or not new_password: st.error("Usuario y contraseña no pueden estar vacíos.")
            elif new_password != confirm_password: st.error("Las contraseñas no coinciden.")
            elif len(new_username) < 3: st.error("El nombre de usuario debe tener al menos 3 caracteres.")
            elif len(new_password) < 6: st.error("La contraseña debe tener al menos 6 caracteres.")
            else:
                if add_user_to_db(new_username, new_password):
                    go_to_page("Login")

elif st.session_state.page == "Dashboard":
    if not st.session_state.logged_in:
        st.warning("Debe iniciar sesión para acceder al dashboard.")
        if st.button("Ir a Login"): go_to_page("Login")
    else:
        st.title(f"Dashboard de Sensores - ¡Bienvenido, {st.session_state.current_user['username']}!")
        st.subheader("Lectura Actual de Entidades en FIWARE Orion")
        if st.button("Refrescar Datos de Orion"): st.rerun()
        entities = get_entities_from_orion()
        if not entities: st.info("No hay entidades disponibles en FIWARE Orion o no se pudo conectar.")
        else:
            st.write(f"Se encontraron {len(entities)} entidades.")
            search_term = st.text_input("Buscar entidad por ID o Tipo:", key="dashboard_search").lower()
            filtered_entities = [e for e in entities if search_term in e.get("id","").lower() or search_term in e.get("type","").lower()] if search_term else entities
            if not filtered_entities and search_term: st.info(f"No se encontraron entidades que coincidan con '{search_term}'.")
            for entity in filtered_entities:
                with st.expander(f"ID: {entity.get('id', 'N/A')} - Tipo: {entity.get('type', 'N/A')}"):
                    st.json(entity)

elif st.session_state.page == "Manage Sensors":
    if not st.session_state.logged_in:
        st.warning("Debe iniciar sesión para acceder a esta página.")
        if st.button("Ir a Login"): go_to_page("Login")
    elif st.session_state.current_user and st.session_state.current_user.get("role") != "admin":
        st.error("Acceso denegado. Solo los administradores pueden gestionar sensores.")
        if st.button("Ir al Dashboard"): go_to_page("Dashboard")
    else:
        st.title("Gestión de Sensores (Entidades en FIWARE Orion)")
        with st.expander("Agregar Nueva Entidad de Tipo 'Sensor'", expanded=False):
            with st.form("add_sensor_form_orion"):
                st.markdown("Crear una nueva entidad con `type: Sensor` en Orion.")
                sensor_name = st.text_input("Nombre descriptivo (atributo 'name')")
                sensor_type_attr = st.selectbox("Tipo de Medición (atributo 'sensorType')", ["Temperatura", "Humedad", "Presión", "Luz", "Movimiento", "CO2", "NivelAgua", "Otro"])
                location = st.text_input("Ubicación (atributo 'location')", placeholder="Ej: Oficina Principal")
                current_value = st.number_input("Valor Actual (atributo 'currentValue')", value=0.0, format="%.2f")
                submit_add = st.form_submit_button("Agregar Sensor a Orion")
                if submit_add:
                    if sensor_name and location:
                        payload = create_sensor_entity_payload(sensor_name, sensor_type_attr, location, current_value)
                        if add_entity_to_orion(payload):
                            st.success(f"Entidad '{payload['id']}' agregada a Orion.")
                            st.rerun()
                    else: st.error("Por favor complete todos los campos (Nombre, Ubicación).")
        st.subheader("Entidades Existentes en Orion")
        all_orion_entities = get_entities_from_orion()
        if not all_orion_entities: st.info("No hay entidades para administrar en FIWARE Orion.")
        else:
            search_admin_term = st.text_input("Buscar entidad para administrar por ID o Tipo:", key="admin_search").lower()
            filtered_admin_entities = [e for e in all_orion_entities if search_admin_term in e.get("id","").lower() or search_admin_term in e.get("type","").lower()] if search_admin_term else all_orion_entities
            if not filtered_admin_entities and search_admin_term: st.info(f"No se encontraron entidades que coincidan con '{search_admin_term}' para administrar.")
            for entity in filtered_admin_entities:
                col1, col2 = st.columns([4, 1])
                entity_id = entity.get("id", "N/A"); entity_type = entity.get("type", "N/A")
                with col1: st.write(f"**ID:** {entity_id} | **Tipo:** {entity_type}")
                with col2:
                    if st.button("🗑️ Eliminar", key=f"del_orion_{entity_id}", help=f"Eliminar {entity_id}"):
                        if delete_entity_from_orion(entity_id):
                            st.success(f"Entidad '{entity_id}' eliminada de Orion.")
                            st.rerun()
else:
    st.error("Página no encontrada.")
    if st.button("Ir a Home"): go_to_page("Home")
