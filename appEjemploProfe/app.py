import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import random
from datetime import datetime, timedelta

IP_ORION = "107.22.120.1"
PORT_ORION = "1026"
# ----------------------------
# Configuración de la página 10.60.24.40, DNS: Gateway 10.60.24.1, 255.255.255.0, 10.100.6.4, 10.100.6.5 
# ----------------------------
st.set_page_config(
    page_title="Mi Proyecto Streamlit",
    layout="wide",
)
st.markdown(
    """
    <style>
      /* Oculta el menú hamburger / Deploy */
      #MainMenu { visibility: hidden; }
      /* Oculta el footer si también quieres quitar “Made with Streamlit” */
      footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)
# ----------------------------
# Datos dummy
# ----------------------------
NEWS = [
    {"title": "Lanzamiento de la plataforma", "description": "Hoy estrenamos nuestra nueva plataforma de monitoreo IoT.", "img_url": "https://www.maherelectronica.com/wp-content/uploads/2021/01/tendencias-tecnologia-agricola.jpg"},
    {"title": "Actualización de sensores", "description": "Se han añadido 5 nuevos sensores de radiación.",       "img_url": "https://www.maherelectronica.com/wp-content/uploads/2021/01/tendencias-tecnologia-agricola.jpg"},
    {"title": "Mantenimiento programado", "description": "Programado mantenimiento este fin de semana.",      "img_url": "https://www.maherelectronica.com/wp-content/uploads/2021/01/tendencias-tecnologia-agricola.jpg"},
]
USER_CREDENTIALS = {"usuario1": "clave123", "admin": "adminpass"}
#funciones para manejar orion con el CRUD
import requests

def crearSensor(ip_servidor: str = "127.0.0.1",puerto_servidor: str = "1026", payload: str = "{}"):
    """
    Publica una entidad NGSI-LD de tipo 'temperatura' en Orion (puerto 1026).
    Si falla la conexión o la petición, devuelve el mensaje de error indicado.

    Args:
        ip_servidor (str): IP del servidor Orion (sin puerto).

    Returns:
        dict | str: JSON de respuesta en caso de éxito, o cadena de error.
    """
    url = f"http://{ip_servidor}:{puerto_servidor}/v2/entities"

    headers = {
        "Content-Type": "application/json"
    }
    print(str(payload))
    print(str(url))
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=5)
        print("se hizo el post")
        resp.raise_for_status()
        print("se obtuvo la respuesta")
        print(str(resp.json()))
        return resp.json()
    except requests.RequestException:
        print("conexion fallida")
        return "no pude conectarme al servidor"

# ----------------------------
# Inicialización de session_state
# ----------------------------
def init_session_state():
    ss = st.session_state
    if "logged_in" not in ss:
        ss.logged_in = False
    if "page" not in ss:
        ss.page = "Login"
    if "carousel_idx" not in ss:
        ss.carousel_idx = 0
    if "sensors" not in ss:
        ss.sensors = [
            {"id": "sensor001", "type": "temperatura", "temperatura":{"value":24.5,"type":"Float"}},
            {"id": "sensor078", "type": "humedad",    "humedad":{"value":67.5,"type":"Float"}},
            {"id": "sensor054", "type": "radiacion_solar",  "radiacionsolar":{"value":1224.5,"type":"Float"}},
        ]
    if "show_create" not in ss:
        ss.show_create = False
    if "confirm_delete_id" not in ss:
        ss.confirm_delete_id = None
    if "confirm_edit_id" not in ss:
        ss.confirm_edit_id = None
    if "edit_id" not in ss:
        ss.edit_id = None

# ----------------------------
# Páginas individuales
# ----------------------------
def login_page():
    st.title("🔒 Iniciar sesión")
    user = st.text_input("Usuario")
    pwd  = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == pwd:
            st.session_state.logged_in = True
            st.session_state.page = "Inicio"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

def logout():
    st.session_state.logged_in = False
    st.session_state.page = "Login"
    st.rerun()

def page_inicio():
    st.title("🏠 Bienvenido a Mi Plataforma IoT")
    st.write("Plataforma para monitorizar sensores de temperatura, humedad y radiación solar.")
    idx = st.session_state.carousel_idx
    news = NEWS[idx]
    st.image(news["img_url"], use_container_width=True)
    st.subheader(news["title"])
    st.write(news["description"])
    c1, c2 = st.columns(2)
    if c1.button("◀ Anterior"):
        st.session_state.carousel_idx = (idx-1) % len(NEWS)
        st.rerun()
    if c2.button("Siguiente ▶"):
        st.session_state.carousel_idx = (idx+1) % len(NEWS)
        st.rerun()

def page_acerca_de():
    st.title("👥 Acerca de")
    creadores = [
        {"name":"Ana Pérez","bio":"Ingeniera electrónica con 10 años en IoT."},
        {"name":"Luis Gómez","bio":"Científico de datos, experto en ML."},
    ]
    for c in creadores:
        st.subheader(c["name"])
        st.write(c["bio"])

def page_tablero():
    st.title("📊 Tablero de Información")
    fechas = [datetime.now() - timedelta(days=i) for i in range(29, -1, -1)]
    df = pd.DataFrame({
        "Temperatura (°C)": [random.uniform(18, 35) for _ in fechas],
        "Humedad (%)":      [random.uniform(30, 80) for _ in fechas],
        "Radiación (W/m²)": [random.uniform(100,800) for _ in fechas],
    }, index=fechas)
    st.line_chart(df, use_container_width=True)

def page_gestion_sensores():
    st.title("⚙ Gestión de Sensores")
    ss = st.session_state
    if st.button("➕ Añadir Sensor"):
        ss.show_create = True
    if ss.show_create:
        with st.expander("Crear Nuevo Sensor", expanded=True):
            n_name = st.text_input("id", key="n_name")
            n_type = st.text_input("type", key="n_type")
            n_param= st.text_input("Parámetro", key="n_param")
            if st.button("Crear", key="create_sensor"):
                mensaje = { "id": n_name,"type": n_type, n_param: { "value": 24.5, "type": "Float"}}
                respuestaorion = crearSensor(ip_servidor="107.22.120.1",puerto_servidor="1026",payload=mensaje) 
                st.text = str(respuestaorion)
                ss.show_create = False
                st.rerun()
    sensors = ss.sensors
    try:
        # GET a /v2/entities con option keyValues para traer sólo valores
        resp = requests.get(
            f"http://{IP_ORION}:{PORT_ORION}/v2/entities",
            params={"options": "keyValues"},
            timeout=5
        )
        resp.raise_for_status()
        sensores = resp.json()
    except requests.RequestException:
        st.error("no pude conectarme al servidor")
        sensores = []
    if sensores:
        st.write("## Lista de Sensores NGSI-v2")
        # __Cabecera manual__
        cols = st.columns([2, 2, 2, 1, 1])
        for header, col in zip(["ID", "Tipo", "Valor", "Borrar", "Suscripción"], cols):
            col.markdown(f"**{header}**")

        for s in sensores:
            # Extraemos valor asumiendo que sólo hay una propiedad aparte de id/type
            props = [k for k in s.keys() if k not in ("id", "type")]
            valor = s[props[0]] if props else None

            cols = st.columns([2, 2, 2, 1, 1])
            cols[0].write(s["id"])
            cols[1].write(s["type"])
            cols[2].write(valor)

            # Botón Borrar
            if cols[3].button("🗑", key=f"del_{s['id']}"):
                try:
                    del_resp = requests.delete(
                        f"http://{IP_ORION}:{PORT_ORION}/v2/entities/{s['id']}",
                        timeout=5
                    )
                    if del_resp.status_code in (204, 200):
                        st.success(f"Sensor {s['id']} borrado")
                    else:
                        st.error(f"Error borrando {s['id']}: {del_resp.status_code}")
                except requests.RequestException:
                    st.error("no pude conectarme al servidor")

            # Botón Crear suscripción
            if cols[4].button("🔔", key=f"sub_{s['id']}"):
                subscription_payload = {
                    "description": f"Subscribir a {s['id']}",
                    "subject": {
                        "entities": [{"id": s["id"], "type": s["type"]}]
                    },
                    "notification": {
                        "http": {"url": "http://<tu-callback-url>/notify"},
                        "attrs": props
                    }
                }
                try:
                    sub_resp = requests.post(
                        f"http://{IP_ORION}:{PORT_ORION}/v2/subscriptions",
                        json=subscription_payload,
                        headers={"Content-Type": "application/json"},
                        timeout=5
                    )
                    if sub_resp.status_code == 201:
                        st.success(f"Suscripción creada para {s['id']}")
                    else:
                        st.error(f"Error suscripción: {sub_resp.status_code}")
                except requests.RequestException:
                    st.error("no pude conectarme al servidor")
    else:
        st.info("No hay sensores para mostrar.")

# ----------------------------
# Flujo principal
# ----------------------------
init_session_state()
if st.session_state.page == "Login":
    login_page()
elif not st.session_state.logged_in:
    st.session_state.page = "Login"
    login_page()
else:
    with st.sidebar:
        selected = option_menu(
            menu_title="Menú de Navegación",
            options=["Inicio", "Acerca de", "Tablero", "Gestión de Sensores", "Logout"],
            icons=["house", "info-circle", "bar-chart", "gear", "box-arrow-right"],
            orientation="vertical",
            styles={"nav-link-selected": {"background-color": "#02ab21"}}
        )
        if selected == "Logout":
            logout()
        else:
            st.session_state.page = selected
    if st.session_state.page == "Inicio":
        page_inicio()
    elif st.session_state.page == "Acerca de":
        page_acerca_de()
    elif st.session_state.page == "Tablero":
        page_tablero()
    elif st.session_state.page == "Gestión de Sensores":
        page_gestion_sensores()
