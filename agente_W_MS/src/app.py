#Integrantes:
#David Romero Rodríguez
#Santiago Gallego Henao

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_DIR = './data'
os.makedirs(DATA_DIR, exist_ok=True)

@app.route('/recibir', methods=['POST'])
def recibir_datos():
    try:
        payload = request.get_json()
        data_to_process = []

        if isinstance(payload, dict):
            data_to_process.append(payload)
        elif isinstance(payload, list):
            data_to_process = payload
        else:
            return jsonify({"error": "Formato JSON inválido"}), 400

        if not data_to_process:
            return jsonify({"error": "No se recibieron datos válidos"}), 400

        processed_files = []
        for item in data_to_process:
            if not isinstance(item, dict):
                continue
            raw_sensor_id = item.get('id')
            if raw_sensor_id is None:
                continue

            sensor_identifier = str(raw_sensor_id).strip()
            if not sensor_identifier or not sensor_identifier.startswith("sensor_w_m_"):
                continue

            file_name = f"{sensor_identifier}.json"
            file_path = os.path.join(DATA_DIR, file_name)

            try:
                with open(file_path, 'w') as f:
                    json.dump(item, f, indent=4)
                processed_files.append(file_name)
                print(f"[{datetime.now()}] Datos guardados en '{file_name}'")
            except Exception as e_file:
                print(f"[{datetime.now()}] Error al guardar '{file_name}': {str(e_file)}")

        return jsonify({
            "status": "ok",
            "message": f"{len(processed_files)} archivos procesados",
            "processed_files": processed_files
        }), 200

    except Exception as e:
        print(f"[{datetime.now()}] Error en /recibir: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6461)