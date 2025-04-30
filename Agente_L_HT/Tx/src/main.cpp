#include <Arduino.h>
#include <ClosedCube_HDC1080.h>
#include <Wire.h>
#include <SPI.h>
#include <LoRa.h>

// Pines LoRa
#define SS 18
#define RST 23
#define DIO0 26

ClosedCube_HDC1080 sensor;

double temperatura = 0;
double humedad = 0;
int id = 1001;

void setup() {
  Serial.begin(115200);
  Wire.begin(0, 4);

  // Iniciar sensor HDC1080
  sensor.begin(0x40);

  // Inicializar LoRa
  Serial.println("Iniciando LoRa...");
  LoRa.setPins(SS, RST, DIO0);
  
  if (!LoRa.begin(915E6)) {
    Serial.println("Error al iniciar LoRa");
    while (1);
  }
  Serial.println("LoRa iniciado");
}

void loop() {
  temperatura = 0;
  humedad = 0;

  Serial.println("Leyendo sensor...");

  for (int i = 0; i < 10; i++) {
    float t = sensor.readTemperature();
    float h = sensor.readHumidity();
    if (isnan(t) || isnan(h)) {
      Serial.println("Error leyendo el sensor");
      return; // Salir del ciclo si hay error de lectura
    }
    temperatura += t;
    humedad += h;
    delay(100);
  }

  temperatura /= 10;
  humedad /= 10;

  String mensaje = "ID=" + String(id) +
                   ";Temp=" + String(temperatura, 2) +
                   ";Hum=" + String(humedad, 2);

  Serial.println("Enviando por LoRa: " + mensaje);

  int result = LoRa.beginPacket();
  if (result == 0) {
    Serial.println("Error: No se pudo comenzar el paquete LoRa.");
  } else {
    Serial.println("Paquete LoRa comenzado.");
  }

  LoRa.print(mensaje);
  
  result = LoRa.endPacket();
  
  if (result == 0) {
    Serial.println("Fallo al enviar paquete LoRa.");
  } else {
    Serial.println("Paquete LoRa enviado exitosamente.");
  }

  // Esperar 5 segundos antes del siguiente ciclo
  Serial.println("Ciclo completado. Esperando 5 segundos...\n");
  delay(5000); // Espera para el siguiente ciclo
  Serial.println("Terminó un ciclo.\n");
}
