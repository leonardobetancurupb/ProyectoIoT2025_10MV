#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266HTTPClient.h>
#include "Ai_AP3216_AmbientLightAndProximity.h"

// Pines del sensor
Ai_AP3216_AmbientLightAndProximity aps = Ai_AP3216_AmbientLightAndProximity(D2, D1);

// Datos WiFi
const char* ssid = "UPBWiFi";
const char* password = "";

// Dirección del servidor Flask (ajústala con la IP pública de tu instancia EC2)
const char* serverUrl = "http://10.38.32.137:6451/recibir"; // Usa /datos si ese es el endpoint en Flask

float mediciones[5];
int contador = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Iniciar WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado");
  Serial.println("IP local: " + WiFi.localIP().toString());

  // Iniciar sensor
  aps.begin();
  aps.startAmbientLightAndProximitySensor();
  Serial.println("Iniciando mediciones continuas de radiación solar...");
}

void loop() {
  long alsValue = aps.getAmbientLight();  // lux
  float irradiancia = alsValue * 0.0079;  // W/m² aproximado
  mediciones[contador] = irradiancia;

  Serial.printf("Medición %d: %.2f W/m²\n", contador + 1, irradiancia);
  contador++;
  delay(1000);

  if (contador == 5) {
    float suma = 0;
    for (int i = 0; i < 5; i++) {
      suma += mediciones[i];
    }
    float promedio = suma / 5.0;

    // JSON con sensor_id
    String sensorId = "sensor_w_rs_003";  // Se cambia este valor por el ID del sensor

    String jsonPayload = "{";
    jsonPayload += "\"sensor_id\": \"" + sensorId + "\", ";
    jsonPayload += "\"RADIACION_SOLAR\": ";
    jsonPayload += String(promedio, 2);
    jsonPayload += "}";

    Serial.println("JSON generado:");
    Serial.println(jsonPayload);

    // Enviar por HTTP POST
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      WiFiClient client;  // <--- Cliente requerido por la nueva API
      http.begin(client, serverUrl);
      http.addHeader("Content-Type", "application/json");
    
      int httpCode = http.POST(jsonPayload);
      if (httpCode > 0) {
        String respuesta = http.getString();
        Serial.printf("Respuesta del servidor [%d]: %s\n", httpCode, respuesta.c_str());
      } else {
        Serial.printf("Error al enviar datos: %s\n", http.errorToString(httpCode).c_str());
      }
    
      http.end();
    } else {
      Serial.println("WiFi no conectado, no se pudo enviar.");
    }

    contador = 0;  // Reiniciar para el siguiente grupo de 5
  }
}
