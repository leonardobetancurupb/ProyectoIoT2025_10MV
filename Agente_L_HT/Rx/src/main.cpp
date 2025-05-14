#include <WiFi.h>
#include <HTTPClient.h>
#include <LoRa.h>
#include "LoRaBoards.h"
 
// WiFi pública
const char* ssid = "UPBWiFi";
const char* password = "";
const char* AGENT_SERVER = "http://ip_publica/data";
 
// Config LoRa
#define CONFIG_RADIO_FREQ         915.0
#define CONFIG_RADIO_OUTPUT_POWER 17
#define CONFIG_RADIO_BW           125.0
 
void setup() {
    Serial.begin(115200);
    delay(1000);
 
    WiFi.begin(ssid,password);
    Serial.print("Conectando a WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi conectado. IP local: " + WiFi.localIP().toString());
 
    setupBoards();
    delay(1500);
 
    Serial.println("LoRa Receiver");
 
#ifdef RADIO_TCXO_ENABLE
    pinMode(RADIO_TCXO_ENABLE, OUTPUT);
    digitalWrite(RADIO_TCXO_ENABLE, HIGH);
#endif
 
    LoRa.setPins(RADIO_CS_PIN, RADIO_RST_PIN, RADIO_DIO0_PIN);
    if (!LoRa.begin(CONFIG_RADIO_FREQ * 1000000)) {
        Serial.println("Fallo al iniciar LoRa!");
        while (1);
    }
 
    LoRa.setTxPower(CONFIG_RADIO_OUTPUT_POWER);
    LoRa.setSignalBandwidth(CONFIG_RADIO_BW * 1000);
    LoRa.setSpreadingFactor(10);
    LoRa.setPreambleLength(16);
    LoRa.setSyncWord(0xAB);
    LoRa.disableCrc();
    LoRa.disableInvertIQ();
    LoRa.setCodingRate4(7);
    LoRa.receive();
}
 
void loop() {
    int packetSize = LoRa.parsePacket();
    if (packetSize) {
        String recv = "";
        while (LoRa.available()) {
            recv += (char)LoRa.read();
        }
 
        Serial.println("Recibido por LoRa: " + recv);
        Serial.println("RSSI: " + String(LoRa.packetRssi()));
 
        // Esperamos formato: p:4471,ip:34.204.1.236,id:sensor_L_RS_001,rs:27.30
        int pIndex = recv.indexOf("p:");
        int ipIndex = recv.indexOf(",ip:");
        int idIndex = recv.indexOf(",id:");
        int rsIndex = recv.indexOf(",rs:");
 
        if (pIndex == -1 || ipIndex == -1 || idIndex == -1 || rsIndex == -1) {
            Serial.println("Formato inválido.");
            return;
        }
 
        int puerto_destino = recv.substring(pIndex + 2, ipIndex).toInt();
        String ip_destino = recv.substring(ipIndex + 4, idIndex);
        String sensor_id = recv.substring(idIndex + 4, rsIndex);
        float lux = recv.substring(rsIndex + 4).toFloat();
 
        Serial.println("Puerto: " + String(puerto_destino));
        Serial.println("IP: " + ip_destino);
        Serial.println("ID: " + sensor_id);
        Serial.println("Lux: " + String(lux, 2));
 
        // Enviar al agente
        if (WiFi.status() == WL_CONNECTED) {
            HTTPClient http;
            http.begin(AGENT_SERVER);
            http.addHeader("Content-Type", "application/json");
 
            String json = "{\"puerto_destino\":" + String(puerto_destino) +
                          ",\"ip_destino\":\"" + ip_destino +
                          "\",\"sensor_id\":\"" + sensor_id +
                          "\",\"lux\":" + String(lux, 2) + "}";
 
            int httpResponseCode = http.POST(json);
 
            if (httpResponseCode > 0) {
                String response = http.getString();
                Serial.println("POST exitoso: " + response);
            } else {
                Serial.println("Error en POST. Código: " + String(httpResponseCode));
            }
 
            http.end();
        } else {
            Serial.println("WiFi desconectado.");
        }
 
        LoRa.receive();
    }
}
