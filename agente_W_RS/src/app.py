from flask import Flask, jsonify, request
from datetime import datetime
import os
import json

app = Flask(__name__)
DATA_FOLDER = '/data'

@app.route('/recibir', methods=['POST'])
def recibir_radiacion():
    data = request.get_json()

    if not data or "RADIACION_SOLAR" not in data or "sensor_id" not in data:
        return jsonify({"error": "JSON inválido o faltante (requiere 'sensor_id' y 'RADIACION_SOLAR')"}), 400

    sensor_id = data["sensor_id"]
    radiacion = data["RADIACION_SOLAR"]

    datos = {
        "sensor_id": sensor_id,
        "RADIACION_SOLAR": radiacion,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    os.makedirs(DATA_FOLDER, exist_ok=True)
    file_path = os.path.join(DATA_FOLDER, f"{sensor_id}.json")

    with open(file_path, 'w') as f:
        json.dump(datos, f, indent=2)

    return jsonify({"mensaje": f"Datos del sensor '{sensor_id}' recibidos correctamente"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6451)
