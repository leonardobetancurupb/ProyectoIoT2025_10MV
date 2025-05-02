#include <SPI.h>
#include <LoRa.h>
#include "LoRaBoards.h"

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

void setup() {
  Serial.begin(115200);
  setupBoards();
  delay(1500);  // estabilización al encender

#ifdef  RADIO_TCXO_ENABLE
  pinMode(RADIO_TCXO_ENABLE, OUTPUT);
  digitalWrite(RADIO_TCXO_ENABLE, HIGH);
#endif

  LoRa.setPins(RADIO_CS_PIN, RADIO_RST_PIN, RADIO_DIO0_PIN);

  if (!LoRa.begin(CONFIG_RADIO_FREQ * 1E6)) {
    Serial.println("Fallo al iniciar LoRa.");
    while (1);
  }

  LoRa.setTxPower(CONFIG_RADIO_OUTPUT_POWER);
  LoRa.setSignalBandwidth(CONFIG_RADIO_BW * 1000);
  LoRa.setSpreadingFactor(10);     // más sensibilidad, menos velocidad
  LoRa.setPreambleLength(16);
  LoRa.setSyncWord(0xAB);
  LoRa.disableCrc();
  LoRa.disableInvertIQ();
  LoRa.setCodingRate4(7);

  Serial.println("LoRa iniciado, esperando mensajes...");
  LoRa.receive();  // modo recepción
}

void loop() {
  int packetSize = LoRa.parsePacket();

  if (packetSize) {
    String mensaje = "";
    while (LoRa.available()) {
      mensaje += (char)LoRa.read();
    }

    Serial.print("Mensaje recibido: ");
    Serial.println(mensaje);
    Serial.print("RSSI: ");
    Serial.print(LoRa.packetRssi());
    Serial.print(" | SNR: ");
    Serial.println(LoRa.packetSnr());

    // Mostrar en OLED si existe
    if (u8g2) {
      char buf[256];
      u8g2->clearBuffer();
      u8g2->drawStr(0, 12, "Mensaje:");
      u8g2->drawStr(0, 26, mensaje.c_str());
      snprintf(buf, sizeof(buf), "RSSI:%i", LoRa.packetRssi());
      u8g2->drawStr(0, 40, buf);
      snprintf(buf, sizeof(buf), "SNR:%.1f", LoRa.packetSnr());
      u8g2->drawStr(0, 56, buf);
      u8g2->sendBuffer();
    }
  }

  delay(100);
}
