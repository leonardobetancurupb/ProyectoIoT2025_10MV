#include <Arduino.h>
#include <Wire.h>
#include <ClosedCube_HDC1080.h>
#include <LoRa.h>

ClosedCube_HDC1080 hdc1080;

// Pines SPI LoRa para TTGO T-Beam
#define LORA_SCK 5
#define LORA_MISO 19
#define LORA_MOSI 27
#define LORA_SS 18
#define LORA_DIO0 26
#define LORA_FREQ 915E6

void setup() {
  Serial.begin(115200);
  while (!Serial);

  // Inicializar sensor HDC1080
  Wire.begin();
  hdc1080.begin(0x40);
  Serial.println("Sensor HDC1080 iniciado");

  // Inicializar LoRa
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

  if (!LoRa.begin(LORA_FREQ)) {
    Serial.println("Error iniciando LoRa. Verifica conexiones.");
    while (true);
  }

  Serial.println("Nodo LoRa en modo receptor (Rx)");
}

void loop() {
  // Esperar paquete entrante
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    Serial.print("Mensaje recibido: ");
    while (LoRa.available()) {
      Serial.print((char)LoRa.read());
    }
    Serial.print(" | RSSI: ");
    Serial.println(LoRa.packetRssi());

    // Leer temperatura y humedad
    float temp = hdc1080.readTemperature();
    float hum = hdc1080.readHumidity();

    Serial.print("Temp: ");
    Serial.print(temp);
    Serial.print(" °C | Hum: ");
    Serial.print(hum);
    Serial.println(" %");
  }

  delay(1000);
}
