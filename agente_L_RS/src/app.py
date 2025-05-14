from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import datetime

app = Flask(__name__)

mongo_url = os.environ.get("MONGO_URL", "mongodb://mongodb:27017/iotdb")
client = MongoClient(mongo_url)
db = client.get_database()
collection = db.sensor_data

@app.route("/data", methods=["POST"])
def receive_data():
    content = request.json
    content["received_at"] = datetime.datetime.utcnow()
    collection.insert_one(content)
    return jsonify({"status": "success"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6451)
