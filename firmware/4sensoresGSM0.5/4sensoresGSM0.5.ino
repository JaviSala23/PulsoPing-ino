#include <SoftwareSerial.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// Pines para los sensores DS18B20
#define ONE_WIRE_BUS_1 9
#define ONE_WIRE_BUS_2 10
#define ONE_WIRE_BUS_3 11  // Pin para el sensor de energía

// Pines para el SIM800L
#define SIM800_TX_PIN 7
#define SIM800_RX_PIN 8

// Pines para los LEDs
#define LED_GREEN_PIN 14
#define LED_RED_PIN 15

// Pin para el transformador de energía
#define ENERGIA_PIN 12  // Pin para detectar energía

// Configuración de la red GSM
const char* apn = "ba.amx";
const char* gprsUser = "clarogprs";  // Puede que sea "" dependiendo del proveedor
const char* gprsPass = "clarogprs999";  // Puede que sea "" dependiendo del proveedor
const char* server = "mantistemp.com.ar";
const uint16_t port = 8000;
const char* path = "/sensor_readings/";

SoftwareSerial sim800(SIM800_RX_PIN, SIM800_TX_PIN);  // Comunicación con SIM800L
OneWire oneWire1(ONE_WIRE_BUS_1);
DallasTemperature sensors1(&oneWire1);

unsigned long lastCommandTime = 0;

void setup() {
  // Configuración serial
  Serial.begin(9600);
  sim800.begin(9600);  // Comunicación con SIM800L
  
  // Inicialización del sensor DS18B20
  sensors1.begin();
  
  // Configuración de pines de LEDs
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_RED_PIN, OUTPUT);
  
  // Configuración del pin de energía
  pinMode(ENERGIA_PIN, INPUT);

  // Configuración del módulo SIM800L
  setupSIM800();
}

void loop() {
  if (millis() - lastCommandTime > 60000) {
    lastCommandTime = millis();
    readSensors();
  }
}

void setupSIM800() {
  sendATCommand("AT", 1000, "OK");  // Comando AT básico para verificar conexión
  sendATCommand("AT+CSQ", 1000, "OK");

  sendATCommand("AT+SAPBR=3,1,\"CONTYPE\",\"GPRS\"", 1000, "OK");  // Configuración GPRS
  sendATCommand("AT+SAPBR=3,1,\"APN\",\"" + String(apn) + "\"", 1000, "OK");  // Establecer APN
  sendATCommand("AT+SAPBR=3,1,\"USER\",\"" + String(gprsUser) + "\"", 1000, "OK");  // Establecer usuario
  sendATCommand("AT+SAPBR=3,1,\"PWD\",\"" + String(gprsPass) + "\"", 1000, "OK");  // Establecer contraseña
  sendATCommand("AT+SAPBR=3,1,\"AUTH\",1", 1000, "OK");  // Establecer autenticación (0: sin autenticación, 1: PAP, 2: CHAP)
  sendATCommand("AT+SAPBR=1,1", 3000, "OK");  // Abrir el contexto GPRS
  sendATCommand("AT+SAPBR=2,1", 1000, "OK");  // Obtener dirección IP
}

void readSensors() {
  sensors1.requestTemperatures();
  float t1 = sensors1.getTempCByIndex(0);
  int puerta = digitalRead(ONE_WIRE_BUS_2);
  int compresor = digitalRead(ONE_WIRE_BUS_3);
  int energia = digitalRead(ENERGIA_PIN);  // Leer el estado del transformador de energía

  if (t1 != DEVICE_DISCONNECTED_C) {
    sendData(t1, puerta, compresor, energia);
  } else {
    Serial.println("Error al leer el sensor DS18B20");
  }
}

void sendData(float temperature, int puerta, int compresor, int energia) {
  String json = "{\"temperature\":" + String(temperature) + ", \"placa\":3, \"puerto\":1, \"puerta_status\":" + String(puerta) + ", \"compresor_status\":" + String(compresor) + ", \"energia_status\":" + String(energia) + "}";

  Serial.println("Enviando datos: " + json);  // Para ver qué datos se están enviando
  
  // Iniciar conexión HTTP
  sendATCommand("AT+HTTPINIT", 1000, "OK");
  sendATCommand("AT+HTTPPARA=\"CID\",1", 1000, "OK");
  sendATCommand("AT+HTTPPARA=\"URL\",\"http://" + String(server) + ":" + String(port) + path + "\"", 1000, "OK");
  sendATCommand("AT+HTTPPARA=\"CONTENT\",\"application/json\"", 1000, "OK");

  sendATCommand("AT+HTTPDATA=" + String(json.length()) + ",10000", 1000, "DOWNLOAD");
  sim800.print(json);
  delay(1000);

  sendATCommand("AT+HTTPACTION=1", 3000, "OK");  // Iniciar POST

  // Leer la respuesta del servidor
  if (sim800.available()) {
    while (sim800.available()) {
      Serial.write(sim800.read());
    }
  } else {
    Serial.println("No hay respuesta del servidor.");
  }

  sendATCommand("AT+HTTPTERM", 1000, "OK");  // Terminar la sesión HTTP
}

void sendATCommand(String command, const int timeout, String expectedResponse) {
  sim800.println(command);
  long int time = millis();
  while ((time + timeout) > millis()) {
    if (sim800.available()) {
      String response = sim800.readString();
      Serial.println("Respuesta: " + response);  // Imprimir la respuesta del SIM800L
      if (response.indexOf(expectedResponse) != -1) {
        Serial.println("Comando OK: " + command);
        return;
      }
    }
  }
  Serial.println("Error en el comando: " + command);  // Si no obtiene la respuesta esperada
}
