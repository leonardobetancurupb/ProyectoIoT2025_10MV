#include <LoRa.h>
#include "LoRaBoards.h"
#include <Wire.h>
#include <ClosedCube_HDC1080.h>

#ifndef CONFIG_RADIO_FREQ
#define CONFIG_RADIO_FREQ           915.0
#endif
#ifndef CONFIG_RADIO_OUTPUT_POWER
#define CONFIG_RADIO_OUTPUT_POWER   17
#endif
#ifndef CONFIG_RADIO_BW
#define CONFIG_RADIO_BW             125.0
#endif

#if !defined(USING_SX1276) && !defined(USING_SX1278)
#error "Este ejemplo solo funciona con radios SX1276/78"
#endif

// Pines I2C para el sensor (ajusta si usas otros)
#define I2C_SDA  0
#define I2C_SCL  4

ClosedCube_HDC1080 sensor;

void setup() {
  setupBoards();
  delay(1500); // tiempo de estabilización

#ifdef RADIO_TCXO_ENABLE
  pinMode(RADIO_TCXO_ENABLE, OUTPUT);
  digitalWrite(RADIO_TCXO_ENABLE, HIGH);
#endif

  Serial.begin(115200);
  Serial.println("LoRa Transmitter con sensor HDC1080...");

  Wire.begin(I2C_SDA, I2C_SCL);
  sensor.begin(0x40);  // Dirección por defecto del HDC1080

  // Inicialización del LoRa
  LoRa.setPins(RADIO_CS_PIN, RADIO_RST_PIN, RADIO_DIO0_PIN);
  if (!LoRa.begin(CONFIG_RADIO_FREQ * 1E6)) {
    Serial.println("❌ Fallo al iniciar LoRa.");
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
}

void loop() {
  // Leer datos del sensor
  float temp = sensor.readTemperature();
  float hum = sensor.readHumidity();

  // Verificar si hay errores
  if (isnan(temp) || isnan(hum)) {
    Serial.println("❌ Error leyendo el sensor HDC1080.");
    delay(2000);
    return;
  }

  // Preparar mensaje
  String mensaje = "Temp=" + String(temp, 2) + " ;Hum=" + String(hum, 2) + " Agente_L_HT" + " Sensor_01";
  Serial.println("📡 Enviando por LoRa: " + mensaje);

  // Transmitir
  int result = LoRa.beginPacket();
  if (result == 0) {
    Serial.println("❌ No se pudo comenzar el paquete LoRa.");
    delay(1000);
    return;
  }

  LoRa.print(mensaje);
  result = LoRa.endPacket();

  if (result == 0) {
    Serial.println("❌ Fallo al enviar el paquete LoRa.");
  } else {
    Serial.println("✅ Paquete enviado exitosamente.");
  }

  delay(5000);  // Esperar antes de la siguiente transmisión
}



