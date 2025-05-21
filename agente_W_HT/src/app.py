from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

@app.route('/6441/recibir', methods=['POST'])
def recibir_dato():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON provided"}), 400

        print("Dato recibido:", data)

        sensor_type = data.get('type', 'default_type')
        raw_id = data.get('id', 'default_id')
        sensor_id = raw_id.replace("SENSOR_", "")  # Elimina prefijo si ya viene incluido

        file_name = f"Agent_{sensor_type}_{sensor_id}.json"
        file_path = os.path.join('/data', file_name)

        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Archivo {file_path} guardado con los datos recibidos.")
        return jsonify({"message": "Dato recibido y guardado correctamente"}), 200

    except Exception as e:
        print("Error al procesar la solicitud:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)