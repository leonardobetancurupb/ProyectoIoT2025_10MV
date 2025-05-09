from flask import Flask, jsonify, render_template_string
import os
import json

app = Flask(__name__)
DATA_FOLDER = '/data'

@app.route('/')
def index():
    # Detectar todos los archivos JSON
    if not os.path.exists(DATA_FOLDER):
        return "No hay datos disponibles", 404

    sensores = []
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith('.json'):
            sensor_id = filename.replace('.json', '')
            sensores.append(sensor_id)

    # HTML básico para mostrar links a sensores
    html_template = """
    <html>
    <head><title>Sensores disponibles</title></head>
    <body>
        <h1>Lista de sensores disponibles</h1>
        <ul>
        {% for sensor in sensores %}
            <li><a href="/{{ sensor }}">{{ sensor }}</a></li>
        {% endfor %}
        </ul>
    </body>
    </html>
    """
    return render_template_string(html_template, sensores=sensores)

@app.route('/<sensor_id>')
def ver_sensor(sensor_id):
    filepath = os.path.join(DATA_FOLDER, f"{sensor_id}.json")
    if not os.path.exists(filepath):
        return jsonify({"error": f"No se encontraron datos para el sensor '{sensor_id}'"}), 404

    with open(filepath, 'r') as f:
        try:
            datos = json.load(f)
        except json.JSONDecodeError:
            return jsonify({"error": "Error al leer JSON"}), 500

    return jsonify(datos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6450)
