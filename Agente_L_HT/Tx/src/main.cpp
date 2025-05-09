#include <Wire.h>
#include <LoRa.h>
#include "LoRaBoards.h"
#include <ClosedCube_HDC1080.h>

#ifndef CONFIG_RADIO_FREQ
#define CONFIG_RADIO_FREQ 915.0
#endif
#ifndef CONFIG_RADIO_OUTPUT_POWER
#define CONFIG_RADIO_OUTPUT_POWER 17
#endif
#ifndef CONFIG_RADIO_BW
#define CONFIG_RADIO_BW 125.0
#endif

#if !defined(USING_SX1276) && !defined(USING_SX1278)
#error "LoRa example is only allowed to run SX1276/78."
#endif

#define MOISTURE_SENSOR_PIN 32
const char *sensorID = "sensor_L_HT_001";
const char *ip_destino = "34.204.1.236";
const int puerto_destino = 6471;

ClosedCube_HDC1080 sensor;

void setup() {
    setupBoards(true);
    delay(1500);
    Serial.begin(115200);

    Wire.begin();
    sensor.begin(0x40);

#ifdef RADIO_TCXO_ENABLE
    pinMode(RADIO_TCXO_ENABLE, OUTPUT);
    digitalWrite(RADIO_TCXO_ENABLE, HIGH);
#endif

    Serial.println("Transmisor LoRa - Humedad y Temperatura");

    LoRa.setPins(RADIO_CS_PIN, RADIO_RST_PIN, RADIO_DIO0_PIN);
    if (!LoRa.begin(CONFIG_RADIO_FREQ * 1000000)) {
        Serial.println("Fallo al iniciar LoRa");
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

    pinMode(MOISTURE_SENSOR_PIN, INPUT);
}

void loop() {
    int humedad = analogRead(MOISTURE_SENSOR_PIN);
    float temperatura = sensor.readTemperature();

    String mensaje = "id:" + String(sensorID) +
                     ",h:" + String(humedad) +
                     ",t:" + String(temperatura, 2) +
                     ",ip:" + String(ip_destino) +
                     ",p:" + String(puerto_destino);

    Serial.println("Enviando por LoRa: " + mensaje);

    LoRa.beginPacket();
    LoRa.print(mensaje);
    LoRa.endPacket();

    delay(30000);  // espera 30 segundos
}
