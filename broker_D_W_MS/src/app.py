#Integrantes:
#David Romero Rodríguez
#Santiago Gallego Henao

from flask import Flask, jsonify, abort, render_template_string
import json
import os
import glob

app = Flask(__name__)
DATA_DIR = './data'

@app.route('/', methods=['GET'])
def listar_sensores_html():
    try:
        if not os.path.exists(DATA_DIR):
            return "<h1>Error: Directorio de datos no encontrado</h1>", 404

        pattern = os.path.join(DATA_DIR, "sensor_w_m_*.json")
        sensor_files_paths = glob.glob(pattern)
        sensor_links = []

        for file_path in sensor_files_paths:
            file_name = os.path.basename(file_path)
            if file_name.startswith("sensor_w_m_") and file_name.endswith(".json"):
                sensor_identifier = file_name[:-5]
                json_url = f"/{sensor_identifier}"
                sensor_links.append({"name": file_name, "id": sensor_identifier, "url": json_url})

        html_template = """
        <html>
        <head><title>Listado de Sensores</title></head>
        <body>
            <h1>Sensores</h1>
            {% if links %}
                <ul>
                    {% for link in links %}
                    <li><strong>{{ link.id }}</strong>: <a href="{{ link.url }}">{{ link.name }}</a></li>
                    {% endfor %}
                </ul>
            {% else %}
                <p>No hay sensores disponibles.</p>
            {% endif %}
        </body>
        </html>
        """
        return render_template_string(html_template, links=sensor_links)
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>", 500

@app.route('/<path:sensor_identifier>', methods=['GET'])
def leer_sensor_especifico(sensor_identifier):
    try:
        if not sensor_identifier.startswith("sensor_w_m_"):
            return jsonify({"error": "ID inválido"}), 404

        file_name = f"{sensor_identifier}.json"
        file_path = os.path.join(DATA_DIR, file_name)

        if not os.path.exists(file_path):
            return jsonify({"error": "Archivo no encontrado"}), 404

        with open(file_path, 'r') as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    app.run(host='0.0.0.0', port=6460)