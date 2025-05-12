#Integrantes:
#David Romero Rodríguez
#Santiago Gallego Henao

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
 
#define HUMEDAD_ANALOG_PIN A0
 
const char* ssid       = "UPBWiFi";
const char* serverUrl  = "http://10.38.32.137:6461/recibir";
 
// Valores calibrados
const int valorSeco   = 1024; // Aire completamente seco (ESP8266 lee 0–1023)
const int valorHumedo = 496;  // Sumergido en agua (mínimo medido)
 
int ultimaLectura      = -1;
const int umbralCambio = 1;   // Solo enviar si cambia ≥1%
 
void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado a WiFi, IP: " + WiFi.localIP().toString());
}
 
void loop() {
  int valorLectura = analogRead(HUMEDAD_ANALOG_PIN);
 
  // Cálculo de porcentaje como float:
  // 0% (seco) cuando valor = valorSeco
  // 100% (mojado) cuando valor = valorHumedo
  float pct = (float)(valorSeco - valorLectura) * 100.0f / (valorSeco - valorHumedo);
  int porcentaje = constrain((int)(pct + 0.5f), 0, 100); // redondea y limita
 
  Serial.print("Crudo: ");
  Serial.print(valorLectura);
  Serial.print(" → Humedad: ");
  Serial.print(porcentaje);
  Serial.println("%");
 
  // Solo enviar si cambió al menos 1%
  if (abs(porcentaje - ultimaLectura) >= umbralCambio) {
    ultimaLectura = porcentaje;
 
    // ==== Preparar JSON ====
    StaticJsonDocument<256> doc;
    doc["id"]   = "sensor_W_MS_001";
    doc["type"] = "humedad";
    JsonObject h = doc.createNestedObject("humedad");
    h["value"]  = porcentaje;
    h["type"]   = "float";
 
    String jsonString;
    serializeJson(doc, jsonString);
    Serial.println("Enviando JSON: " + jsonString);
 
    // ==== Envío HTTP ====
    if (WiFi.status() == WL_CONNECTED) {
      WiFiClient wifiClient;
      HTTPClient http;
      http.begin(wifiClient, serverUrl);
      http.addHeader("Content-Type", "application/json");
      int code = http.POST(jsonString);
 
      if (code > 0) {
        Serial.println("HTTP Response code: " + String(code));
      } else {
        Serial.println("Error HTTP: " + http.errorToString(code));
      }
      http.end();
    }
  }
 
  delay(5000);
}