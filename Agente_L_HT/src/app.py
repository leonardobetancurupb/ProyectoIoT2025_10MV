from flask import Flask, request
from crate import client

app = Flask(__name__)

@app.route('/')
def home():
    conn = client.connect("http://crate-db:4200", username="crate")
    cursor = conn.cursor()
    cursor.execute("SELECT time_index, temperatura FROM ettemperatura WHERE entity_id='sensor001' ORDER BY time_index DESC LIMIT 10")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return str(rows)

if __name__ == '__main__':
        app.run(debug=True,host='0.0.0.0',port=80)