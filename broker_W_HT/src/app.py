from flask import Flask, jsonify, request, send_from_directory, render_template_string
import os
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def obtener_todos():
    try:
        data_folder = '/data'
        json_files = [f for f in os.listdir(data_folder) if f.endswith('.json')]

        # Generar HTML dinámico
        html_content = "<h1>Archivos JSON disponibles</h1><ul>"
        for file in json_files:
            name = file.replace('.json', '')
            html_content += f'<li><a href="/{name}">{file}</a></li>'
        html_content += "</ul>"

        return render_template_string(html_content), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/<name>', methods=['GET'])
def obtener_uno(name):
    try:
        file_name = f"{name}.json"
        file_path = os.path.join('/data', file_name)

        if not os.path.exists(file_path):
            return jsonify({"error": f"Archivo '{file_name}' no encontrado"}), 404

        with open(file_path, 'r') as json_file:
            content = json.load(json_file)
        return jsonify(content), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)