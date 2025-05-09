# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import os
import json
from collections import OrderedDict
from datetime import datetime
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Directorio donde guardar los datos
DATA_FOLDER = './data'
os.makedirs(DATA_FOLDER, exist_ok=True)

@app.route('/recibir', methods=['POST'])
def recibir():
    try:
        raw = request.get_json(force=True)
        logger.info(f"Datos recibidos: {raw}")
        
        # Extraer datos del mensaje LoRa
        sensor_id = raw.get("id", "")
        humedad = raw.get("h", None)
        
        if not sensor_id or humedad is None:
            logger.warning(f"Datos incompletos recibidos: {raw}")
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        # Construcción del JSON con orden forzado
        ordenado = OrderedDict()
        ordenado["id"] = sensor_id
        ordenado["type"] = "L_M"  # LoRa Moisture
        ordenado["humedad"] = OrderedDict([
            ("value", float(humedad)),
            ("type", "Float")
        ])
        ordenado["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        filepath = os.path.join(DATA_FOLDER, f"{sensor_id}.json")
        with open(filepath, 'w') as f:
            json.dump(ordenado, f, indent=2)
        
        logger.info(f"Datos guardados para sensor {sensor_id}")
        return jsonify({"status": "ok", "message": f"Dato de {sensor_id} guardado"}), 200
    except Exception as e:
        logger.error(f"Error al procesar datos: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6491) 