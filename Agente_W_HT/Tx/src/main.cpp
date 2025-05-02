#include <Arduino.h>
#include <Wire.h>
#include <ClosedCube_HDC1080.h>

ClosedCube_HDC1080 sensor;

double listaMediciones[10] = {0}; // Almacena las mediciones de temperatura
double sumaMediciones = 0;  // Suma acumulada de mediciones
double promedio = 0;  // Media de temperatura calculada
int n = 0;  // Contador de mediciones
int id = 1;  // Identificador del ciclo de medición

enum Estado {S, A, B, C, D}; 
Estado estado = S; 

void setup() {
  Serial.begin(115200);
  sensor.begin(0x40);  
  Serial.println("Iniciando sensor HDC1080...");
  estado = A; // Primer estado al iniciar
}

// Estado A: Toma 10 mediciones de temperatura y acumula la suma
void stateA() {
  if (n < 10) {
    delay(10);
    double temp = sensor.readTemperature();
    listaMediciones[n] = temp;
    sumaMediciones += temp;  // Acumula la suma directamente
    Serial.print("Temperatura = ");
    Serial.print(temp);
    Serial.println(" ºC");
    n++;
  } else {
    estado = B; // Cuando se completan 10 mediciones, pasa al siguiente estado
  }
}

// Estado B: Calcula la media usando la suma acumulada
void stateB() {
  promedio = sumaMediciones / 10.0;
  Serial.print("Media de las mediciones = ");
  Serial.print(promedio);
  Serial.println(" ºC");

  estado = C; // Pasa al estado C
}

// Estado C: Imprime el ID, la media y el mensaje "Transmit"
void stateC() {
  Serial.print("ID: ");
  Serial.print(id);
  Serial.print(" | Media: ");
  Serial.print(promedio);
  Serial.println(" | Transmit");

  id++; // Incrementa el identificador del ciclo
  estado = D; // Pasa al estado D
}

// Estado D: Espera 50 segundos antes de reiniciar el proceso
void stateD() {
  Serial.println("Estoy durmiendo por 50 segundos...");
  delay(5000);
  n = 0; // Reinicia el contador de mediciones
  sumaMediciones = 0; // Reinicia la suma acumulada
  estado = A; // Retorna al estado A para iniciar un nuevo ciclo
}

void loop() {
  switch (estado) {
    case A: stateA(); break;
    case B: stateB(); break;
    case C: stateC(); break;
    case D: stateD(); break;
    default: break;
  }
}
