from flask import Flask, request
import crate.client  # Cliente de CrateDB

# Crear la app Flask
app = Flask(__name__)

shift = 1

# Conectar a CrateDB usando el nombre del servicio en Docker Compose
def get_db_connection():
    # Aquí usamos "crate-db" como el nombre del contenedor, tal como está en el docker-compose.yml
    conn = crate.client.connect('crate-db:5432')  # Conexión a CrateDB a través del servicio 'crate-db'
    return conn

# Función de descifrado (Cifrado César)
def decryptString(message, shift):
    decryptedMessage = ""
    for c in message:
        if c.isalpha():
            base = 'A' if c.isupper() else 'a'
            c = chr((ord(c) - ord(base) - shift) % 26 + ord(base))  # Desplazamiento para letras
        decryptedMessage += c
    return decryptedMessage

last_decrypted_data = ""

@app.route('/')
def home():
    global last_decrypted_data
    if last_decrypted_data:
        return f"Últimos datos descifrados: {last_decrypted_data}"
    else:
        return "No hay datos descifrados disponibles aún."

@app.route('/sensordata', methods=['POST'])
def receive_sensor_data():
    # Recibir los datos cifrados como texto
    encrypted_data = request.data.decode('utf-8')  # Los datos llegan como texto cifrado

    # Descifrar los datos
    decrypted_data = decryptString(encrypted_data, shift)

    # Mostrar los datos descifrados
    print(f"Datos cifrados recibidos: {encrypted_data}")
    print(f"Datos descifrados: {decrypted_data}")

    # Guardar el dato descifrado en la variable global
    global last_decrypted_data
    last_decrypted_data = decrypted_data

    # Conectar a CrateDB e insertar los datos
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Crear la tabla si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        encrypted_data TEXT,
        decrypted_data TEXT
    )
    """)

    # Insertar los datos cifrados y descifrados en CrateDB
    cursor.execute("""
    INSERT INTO sensor_data (encrypted_data, decrypted_data)
    VALUES (?, ?)
    """, (encrypted_data, decrypted_data))

    conn.commit()
    cursor.close()

    return "Datos recibidos, descifrados e insertados en CrateDB correctamente", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

