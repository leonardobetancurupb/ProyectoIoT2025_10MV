from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Conexión a MongoDB
mongo_url = os.environ.get("MONGO_URL", "mongodb://mongodb:27017/iotdb")
client = MongoClient(mongo_url)
db = client.get_database()
collection = db.sensor_data

# GET / → HTML con lista de sensores
@app.route("/", methods=["GET"])
def list_sensors():
    sensores = collection.distinct("sensor_id")
    html = "<h1>Sensores registrados</h1><ul>"
    for sensor in sensores:
        html += f'<li><a href="/{sensor}">{sensor}</a></li>'
    html += "</ul>"
    return html

# GET /<sensor_id> → JSON del último valor
@app.route("/<sensor_id>", methods=["GET"])
def sensor_data(sensor_id):
    doc = collection.find_one(
        {"sensor_id": sensor_id},
        sort=[("received_at", -1)]
    )
    if doc:
        return jsonify({
            "id": sensor_id,
            "RS": {
                "type": "Float",
                "value": round(doc.get("lux", 0.0), 2)
            }
        })
    else:
        return jsonify({"error": "Sensor no encontrado"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6450)