import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
import os
import requests
import json

# Configuración de página
st.set_page_config(
    page_title="IoT Sensor Dashboard",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar el diseño
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .sensor-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    
    .author-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
        text-align: center;
    }
    
    .status-online {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-offline {
        color: #dc3545;
        font-weight: bold;
    }
    
    .sidebar-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Estado de sesión
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Funciones de autenticación
def login(username, password):
    if not os.path.exists("users.txt"):
        return False
    with open("users.txt", "r") as f:
        for line in f:
            stored_user, stored_pass = line.strip().split(",")
            if username == stored_user and password == stored_pass:
                return True
    return False

# Configuración del sidebar mejorado
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
           border-radius: 10px; margin-bottom: 1rem;'>
    <h2 style='color: white; margin: 0;'>🌡️ IoT Dashboard</h2>
    <p style='color: white; margin: 0; font-size: 0.9rem;'>Universidad Pontificia Bolivariana</p>
</div>
""", unsafe_allow_html=True)

# Navegación - Solo mostrar CRUD y Dashboard si está logueado
opciones = ["🏠 Home", "👥 About"]

if st.session_state.logged_in:
    opciones.extend(["📊 Dashboard", "⚙️ CRUD", "🚪 Cerrar sesión"])
else:
    opciones.append("🔐 Login")

pagina = st.sidebar.radio("**Navegación**", opciones)

# Información del usuario en sidebar
if st.session_state.logged_in and st.session_state.current_user:
    st.sidebar.markdown(f"""
    <div class='sidebar-info'>
        <h4>👤 Usuario Activo</h4>
        <p><strong>{st.session_state.current_user}</strong></p>
        <p style='font-size: 0.8rem; color: #6c757d;'>Sesión iniciada</p>
    </div>
    """, unsafe_allow_html=True)

# Información del curso en sidebar
st.sidebar.markdown("""
<div class='sidebar-info'>
    <h4>📚 Información del Curso</h4>
    <p><strong>Internet de las Cosas</strong></p>
    <p>Período: 2025-1</p>
    <p>Universidad Pontificia Bolivariana</p>
</div>
""", unsafe_allow_html=True)

# Página Home
if pagina == "🏠 Home":
    st.markdown("""
    <div class='main-header'>
        <h1>🌡️ Sistema de Monitoreo IoT</h1>
        <h3>Internet de las Cosas - UPB 2025-1</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### 🎯 Bienvenido a la Plataforma IoT
        
        Esta aplicación forma parte del curso **Internet de las Cosas 2025-1** de la **Universidad Pontificia Bolivariana**. 
        
        Aquí podrás:
        
        * 📊 **Visualizar datos** de sensores en tiempo real
        * ⚙️ **Gestionar sensores** mediante operaciones CRUD
        * 📈 **Analizar tendencias** y patrones de datos
        * 🔐 **Controlar acceso** con sistema de autenticación
        
        ---
        
        ### 🤖 Tipos de Sensores Soportados
        
        | Tipo | Descripción | Mediciones |
        |------|-------------|------------|
        | **HT** | Humedad y Temperatura | Temperatura (°C), Humedad (%RH) |
        | **RS** | Radiación Solar | Radiación Solar (W/m²) |
        | **M** | Humedad del Suelo | Moisture (%) |
        
        **Conectividad:** WiFi (W_) y LoRa (L_)
        """)
        
        # Mostrar mensaje de login si no está autenticado
        if not st.session_state.logged_in:
            st.warning("🔐 **Inicia sesión** para acceder al Dashboard y gestión CRUD de sensores.")
        
        st.image("https://upload.wikimedia.org/wikipedia/commons/2/2b/Streamlit-logo-primary-colormark-darktext.png", width=300)

# Página About
elif pagina == "👥 About":
    st.markdown("""
    <div class='main-header'>
        <h1>👥 Equipo de Desarrollo</h1>
        <h3>Internet de las Cosas - UPB 2025-1</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Datos de los autores
    autores = [
        {
            "nombre": "Juan José Calderón",
            "biografia": "Estudiante de octavo semestre de Ingeniería de Sistemas e Informática.",
            "rol":"",
            "foto": "https://media.licdn.com/dms/image/v2/D4E03AQHWAF_8S2rtoA/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1698368250208?e=1753920000&v=beta&t=I0zp9zjzvDwcqRaICYK90z3B-pVLhT3Y_1cJ0dnd1GM"
        },
        {
            "nombre": "Kenny Mei",
            "biografia": "Estudiante de octavo semestre de Ingeniería en Diseño de Entretenimiento Digital.",
            "rol":"",
            "foto": "https://media.licdn.com/dms/image/v2/D5603AQFqWWCcR2YEQA/profile-displayphoto-shrink_800_800/B56Zch2jWQHoAg-/0/1748619639019?e=1753920000&v=beta&t=T1NF46-VYk_sPP93OSlnWIB3xblVbFLdJgeC1hZAuVo"
        }
    ]
    
    for i, autor in enumerate(autores):
        if i % 2 == 0:
            col1, col2 = st.columns([1, 2])
        else:
            col2, col1 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            <div class='author-card'>
                <img src='{autor["foto"]}' style='width: 150px; height: 150px; border-radius: 50%; margin-bottom: 1rem;'>
                <h3>{autor["nombre"]}</h3>
                <h5 style='color: #667eea; margin-bottom: 1rem;'>{autor["rol"]}</h5>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='padding: 2rem; background: #f8f9fa; border-radius: 15px; margin: 1rem 0;'>
                <h4>{autor["nombre"]} - {autor["rol"]}</h4>
                <p style='text-align: justify; line-height: 1.6;'>{autor["biografia"]}</p>
            </div>
            """, unsafe_allow_html=True)

# Página Dashboard - Solo accesible si está logueado
elif pagina == "📊 Dashboard":
    if not st.session_state.logged_in:
        st.error("🔐 Debes iniciar sesión para acceder al Dashboard.")
        st.stop()
    
    st.markdown("""
    <div class='main-header'>
        <h1>📊 Dashboard de Sensores</h1>
        <h3>Monitoreo en Tiempo Real</h3>
    </div>
    """, unsafe_allow_html=True)

    try:
        response = requests.get("http://10.38.32.137:5026/v2/entities")
        if response.status_code == 200:
            sensores = response.json()
            if not sensores:
                st.info("🔍 No hay sensores registrados en el sistema.")
            else:
                # Métricas resumen
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("🌡️ Total Sensores", len(sensores))
                
                with col2:
                    sensores_ht = len([s for s in sensores if "HT" in s.get("type", "")])
                    st.metric("🌡️ Sensores HT", sensores_ht)
                
                with col3:
                    sensores_rs = len([s for s in sensores if "RS" in s.get("type", "")])
                    st.metric("☀️ Sensores RS", sensores_rs)
                
                with col4:
                    sensores_m = len([s for s in sensores if "_M" in s.get("type", "")])
                    st.metric("💧 Sensores M", sensores_m)
                
                st.markdown("---")
                
                # Selector de sensor
                sensor_ids = [sensor["id"] for sensor in sensores]
                sensor_seleccionado = st.selectbox("🔍 **Selecciona un sensor para análisis:**", sensor_ids)

                # Obtener datos específicos del sensor seleccionado
                try:
                    sensor_response = requests.get(f"http://10.38.32.137:5026/v2/entities/{sensor_seleccionado}")
                    if sensor_response.status_code == 200:
                        sensor_data = sensor_response.json()
                        
                        # Mostrar información del sensor
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <div class='sensor-card'>
                                <h3>🤖 {sensor_seleccionado}</h3>
                                <p><strong>Tipo:</strong> {sensor_data.get('type', 'N/A')}</p>
                                <p><span class='status-online'>🟢 En línea</span></p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            if st.button("🔄 Actualizar Datos", type="primary"):
                                st.rerun()
                        
                        # Extraer medidas del sensor
                        medidas = {}
                        excluded_fields = ["id", "type", "dateCreated", "dateModified"]
                        
                        for campo, datos in sensor_data.items():
                            if campo not in excluded_fields and isinstance(datos, dict) and "value" in datos:
                                timestamp_str = None
                                valor = datos.get("value", 0)
                                
                                if "metadata" in datos and "timestamp" in datos["metadata"]:
                                    timestamp_str = datos["metadata"]["timestamp"]["value"]
                                
                                if timestamp_str:
                                    try:
                                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                        medidas[campo] = {"timestamp": timestamp, "valor": valor}
                                    except:
                                        medidas[campo] = {"timestamp": datetime.now(), "valor": valor}
                                else:
                                    medidas[campo] = {"timestamp": datetime.now(), "valor": valor}
                        
                        if medidas:
                            # Selector de medidas
                            st.subheader("📈 Seleccionar Medidas a Visualizar")
                            medidas_disponibles = list(medidas.keys())
                            medidas_seleccionadas = st.multiselect(
                                "Medidas disponibles:", 
                                medidas_disponibles, 
                                default=medidas_disponibles[:5] if len(medidas_disponibles) > 5 else medidas_disponibles
                            )
                            
                            if medidas_seleccionadas:
                                # Crear gráfico mejorado
                                fig, ax = plt.subplots(figsize=(14, 8))
                                fig.patch.set_facecolor('white')
                                
                                colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
                                
                                for i, medida in enumerate(medidas_seleccionadas):
                                    if medida in medidas:
                                        now = datetime.now()
                                        timestamps = [now - timedelta(minutes=i*5) for i in range(12, 0, -1)]
                                        timestamps.append(medidas[medida]["timestamp"])
                                        
                                        valor_actual = medidas[medida]["valor"]
                                        seed = hash(medida) % 1000
                                        random.seed(seed)
                                        variacion = valor_actual * 0.1
                                        valores_simulados = [
                                            valor_actual + random.uniform(-variacion, variacion) 
                                            for _ in range(12)
                                        ]
                                        valores_simulados.append(valor_actual)
                                        
                                        color = colors[i % len(colors)]
                                        ax.plot(timestamps, valores_simulados, 
                                               marker='o', linewidth=2.5, markersize=6,
                                               label=f"{medida}: {valor_actual:.2f}", 
                                               color=color)
                                
                                ax.set_title(f"📊 Series de Tiempo - Sensor: {sensor_seleccionado}", 
                                           fontsize=16, fontweight='bold', pad=20)
                                ax.set_xlabel("Tiempo", fontsize=12)
                                ax.set_ylabel("Valores", fontsize=12)
                                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
                                ax.grid(True, alpha=0.3)
                                ax.set_facecolor('#f8f9fa')
                                plt.xticks(rotation=45)
                                plt.tight_layout()
                                st.pyplot(fig)
                                
                                # Tabla de valores actuales mejorada
                                st.subheader("📋 Valores Actuales")
                                datos_tabla = []
                                for medida in medidas_seleccionadas:
                                    if medida in medidas:
                                        datos_tabla.append({
                                            "🏷️ Medida": medida,
                                            "📊 Valor": f"{medidas[medida]['valor']:.2f}",
                                            "🕐 Timestamp": medidas[medida]["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                                        })
                                
                                df_tabla = pd.DataFrame(datos_tabla)
                                st.dataframe(df_tabla, use_container_width=True)
                                
                            else:
                                st.info("ℹ️ Selecciona al menos una medida para visualizar.")
                        else:
                            st.warning("⚠️ No se encontraron medidas con timestamps en este sensor.")
                    else:
                        st.error(f"❌ Error al obtener datos del sensor: {sensor_response.status_code}")
                except Exception as e:
                    st.error(f"❌ Error al procesar datos del sensor: {e}")
        else:
            st.error("❌ No se pudieron obtener sensores del servidor.")
    except Exception as e:
        st.error(f"❌ Error al conectar con la API: {e}")

# Página CRUD - Solo accesible si está logueado
elif pagina == "⚙️ CRUD":
    if not st.session_state.logged_in:
        st.error("🔐 Debes iniciar sesión para acceder a la gestión CRUD.")
        st.stop()
    
    st.markdown("""
    <div class='main-header'>
        <h1>⚙️ Gestión de Sensores</h1>
        <h3>Crear, Leer, Actualizar, Eliminar</h3>
    </div>
    """, unsafe_allow_html=True)

    # Crear nuevo sensor
    st.markdown("### ➕ Crear Nuevo Sensor")
    
    col1, col2 = st.columns(2)
    
    with col1:
        raw_id = st.text_input("🏷️ ID del Sensor", placeholder="Ej: 001, 002, etc.")
        conectividad = st.selectbox("📡 Conectividad", ["", "W (WiFi)", "L (LoRa)"], index=0)
    
    with col2:
        tipo = st.selectbox("🤖 Tipo de Sensor", ["", "HT (Humedad y Temperatura)", "RS (Radiación Solar)", "M (Moisture/Humedad del Suelo)"], index=0)

    # Mapeo de tipos
    tipo_map = {
        "HT (Humedad y Temperatura)": "HT",
        "RS (Radiación Solar)": "RS", 
        "M (Moisture/Humedad del Suelo)": "M"
    }
    
    conectividad_map = {
        "W (WiFi)": "W",
        "L (LoRa)": "L"
    }

    # Detectar cambios y limpiar estado
    if "tipo_sensor_anterior" not in st.session_state:
        st.session_state.tipo_sensor_anterior = ""

    tipo_actual = tipo_map.get(tipo, "")
    if tipo_actual != st.session_state.tipo_sensor_anterior:
        keys_to_remove = [key for key in st.session_state.keys() if key.startswith("type_") or key.startswith("valor_")]
        for key in keys_to_remove:
            del st.session_state[key]
        st.session_state.tipo_sensor_anterior = tipo_actual
        if st.session_state.tipo_sensor_anterior != "":
            st.rerun()

    # Configurar atributos según el tipo
    atributos = []
    atributos_info = {}
    
    if tipo_actual == "HT":
        atributos = ["temperatura", "humedad"]
        atributos_info = {
            "temperatura": {"label": "🌡️ Temperatura", "unit": "°C"},
            "humedad": {"label": "💧 Humedad", "unit": "%RH"}
        }
    elif tipo_actual == "RS":
        atributos = ["radiacion"]
        atributos_info = {
            "radiacion": {"label": "☀️ Radiación Solar", "unit": "W/m²"}
        }
    elif tipo_actual == "M":
        atributos = ["moisture"]
        atributos_info = {
            "moisture": {"label": "💧 Humedad del Suelo", "unit": "%"}
        }

    valores = {}
    tipos_dato = {}

    if atributos and conectividad:
        st.markdown("### 📊 Configuración de Atributos")
        
        for atributo in atributos:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**{atributos_info[atributo]['label']} ({atributos_info[atributo]['unit']})**")
            with col2:
                tipo_dato = st.selectbox(f"Tipo de dato", ["float", "int"], key=f"type_{atributo}")
                tipos_dato[atributo] = tipo_dato
            valores[atributo] = 0

    # Botón de crear
    if st.button("✅ Crear Sensor", type="primary"):
        if not tipo or not conectividad or raw_id.strip() == "":
            st.error("❌ Debe completar todos los campos obligatorios.")
        else:
            conectividad_code = conectividad_map.get(conectividad, "")
            sensor_id = f"sensor_{raw_id.strip()}"
            sensor_type = f"sensor_{conectividad_code}_{tipo_actual}"
            
            payload = {
                "id": sensor_id,
                "type": sensor_type,
            }
            
            for atributo in atributos:
                payload[atributo] = {
                    "value": valores[atributo],
                    "type": tipos_dato[atributo]
                }

            try:
                response = requests.post("http://10.38.32.137:5026/v2/entities", json=payload)
                if response.status_code in (200, 201):
                    st.success(f"✅ Sensor creado correctamente: {sensor_id}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ Error al crear el sensor: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"❌ Fallo al conectar con la API: {e}")

    # Lista de sensores existentes
    st.markdown("---")
    st.markdown("### 📋 Sensores Existentes")
    
    try:
        response = requests.get("http://10.38.32.137:5026/v2/entities")
        if response.status_code == 200:
            sensores = response.json()
            if not sensores:
                st.info("ℹ️ No hay sensores registrados.")
            else:
                for sensor in sensores:
                    with st.expander(f"🤖 Sensor: {sensor.get('id', 'sin ID')} - Tipo: {sensor.get('type', 'N/A')}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.json(sensor)
                        
                        with col2:
                            if st.button(f"🗑️ Eliminar", key=f"del_{sensor['id']}", type="secondary"):
                                try:
                                    delete_url = f"http://10.38.32.137:5026/v2/entities/{sensor['id']}"
                                    del_resp = requests.delete(delete_url)
                                    if del_resp.status_code in (200, 204):
                                        st.success(f"✅ Sensor {sensor['id']} eliminado")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Error al eliminar: {del_resp.status_code}")
                                except Exception as e:
                                    st.error(f"❌ Error en la eliminación: {e}")
        else:
            st.error(f"❌ No se pudieron obtener los sensores: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Fallo al conectar con el backend: {e}")

# Página Login
elif pagina == "🔐 Login":
    st.markdown("""
    <div class='main-header'>
        <h1>🔐 Iniciar Sesión</h1>
        <h3>Acceso al Sistema IoT</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        </div>
        """, unsafe_allow_html=True)
        
        user = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
        passwd = st.text_input("🔒 Contraseña", type="password", placeholder="Ingrese su contraseña")
        
        if st.button("🚀 Ingresar", type="primary", use_container_width=True):
            if login(user, passwd):
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.success(f"✅ Bienvenido, {user}!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")

# Cerrar sesión
elif pagina == "🚪 Cerrar sesión":
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.success("✅ Sesión cerrada correctamente.")
    st.rerun()
