from flask import Flask, jsonify, render_template, abort
import pandas as pd
import numpy as np
from collections import OrderedDict
import os
import json
import requests

app = Flask(__name__)

# Directorio donde se almacenan los archivos JSON de los sensores
SENSORS_DIR = "./data"
AGENT_URL = "http://agente:6491"  # URL del agente

def preprocess_file(sensor_file):
    """Preprocesa un archivo JSON de sensor y lo guarda sobrescribiendo"""
    try:
        path = os.path.join(SENSORS_DIR, sensor_file)
        with open(path, 'r') as f:
            data = json.load(f)

        df = pd.json_normalize(data)

        # Convertir a numérico
        df['humedad.value'] = pd.to_numeric(df.get('humedad.value', np.nan), errors='coerce')

        # Filtrado de atípicos
        df['humedad.value'] = df['humedad.value'].apply(lambda x: np.nan if (x < 0 or x > 100) else x)

        # Relleno de nulos con media
        df['humedad.value'].fillna(df['humedad.value'].mean(), inplace=True)

        # Corrección de valores categóricos
        df['id'] = df['id'].apply(lambda x: "lora" if x != "lora" else x)
        df['type'] = df['type'].apply(lambda x: "L_M" if x != "L_M" else x)
        df['humedad.type'] = df['humedad.type'].apply(lambda x: "Float" if x != "Float" else x)

        # Crear estructura anidada
        df['humedad'] = df.apply(lambda x: {'type': x['humedad.type'], 'value': x['humedad.value']}, axis=1)

        # Eliminar columnas planas
        df.drop(['humedad.type', 'humedad.value'], axis=1, inplace=True)

        # Sobrescribir archivo
        with open(path, 'w') as f:
            json.dump(df.to_dict(orient='records'), f, indent=4)

    except Exception as e:
        print(f"Error procesando {sensor_file}: {e}")

def preprocess_all():
    """Preprocesa todos los archivos de sensores en la carpeta"""
    if not os.path.exists(SENSORS_DIR):
        return
    for filename in os.listdir(SENSORS_DIR):
        if filename.endswith('.json'):
            preprocess_file(filename)

def get_sensor_list():
    """Obtiene la lista de sensores disponibles a partir de los archivos JSON"""
    try:
        # Verifica si el directorio existe
        if not os.path.exists(SENSORS_DIR):
            return []
        
        # Lista todos los archivos JSON en el directorio
        sensors = []
        for filename in os.listdir(SENSORS_DIR):
            if filename.endswith('.json'):
                sensor_name = filename.replace('.json', '')
                sensors.append(sensor_name)
        
        return sensors
    except Exception as e:
        print(f"Error al listar sensores: {str(e)}")
        return []

def get_sensor_data(sensor_name):
    """Obtiene los datos de un sensor específico"""
    try:
        file_path = os.path.join(SENSORS_DIR, f"{sensor_name}.json")
        
        # Verifica si el archivo existe
        if not os.path.exists(file_path):
            return None
        
        # Lee y devuelve el contenido del archivo JSON
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        return data
    except Exception as e:
        print(f"Error al leer datos del sensor {sensor_name}: {str(e)}")
        return None

def generate_sensors_html(sensors):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Listado de Sensores de Humedad</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 10px 0; padding: 10px; background-color: #f7f7f7; border-radius: 5px; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .sensor-value { float: right; color: #666; }
        </style>
    </head>
    <body>
        <h1>Listado de Sensores de Humedad</h1>
        <ul>
    """
    
    for sensor in sensors:
        data = get_sensor_data(sensor)
        if data and isinstance(data, list) and len(data) > 0:
            last_value = data[-1].get('humedad', {}).get('value', 'N/A')
            html += f'<li><a href="/{sensor}">{sensor}</a><span class="sensor-value">Última lectura: {last_value}%</span></li>'
        else:
            html += f'<li><a href="/{sensor}">{sensor}</a><span class="sensor-value">Sin datos</span></li>'
    
    html += """
        </ul>
    </body>
    </html>
    """
    return html

@app.route('/', methods=['GET'])
def list_sensors():
    """Ruta principal que muestra la lista de sensores disponibles"""
    preprocess_all()  # Preprocesa todos los archivos JSON al iniciar
    sensors = get_sensor_list()
    html = generate_sensors_html(sensors)
    return html

@app.route('/<sensor_name>', methods=['GET'])
def get_sensor(sensor_name):
    """Ruta dinámica que muestra los datos de un sensor específico"""
    sensor_data = get_sensor_data(sensor_name)
    
    if sensor_data is None:
        abort(404, description=f"Sensor '{sensor_name}' no encontrado")
        
    return jsonify(sensor_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6490, debug=True) 