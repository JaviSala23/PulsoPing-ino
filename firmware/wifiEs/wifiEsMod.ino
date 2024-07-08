#include <ESP8266WiFi.h>
#include <DHT.h>

// Definir detalles del sensor y del servidor (asumiendo que están fijos)
#define DHTPIN 4
#define DHTTYPE DHT22
const char* host = "habitatonline.ar";
const uint16_t port = 801;
const char* path = "/sensor-readings/";

DHT dht(DHTPIN, DHTTYPE);
WiFiClient client;

char ssid[32];      // Arreglo de caracteres para SSID
char password[32];  // Arreglo de caracteres para contraseña

// Prototipos de funciones
void setup();
void loop();
void configureWiFi();
void connectToWiFi();
void sendRequest(String request);

void setup() {
  Serial.begin(115200);
  dht.begin();

  Serial.println("ESP8266 DHT Sensor Data to Server");

  // Leer SSID y contraseña desde el puerto serial
  configureWiFi();

  connectToWiFi();
}

void loop() {
  // Leer temperatura y humedad
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Verificar errores en la lectura del sensor
  if (isnan(h) || isnan(t)) {
    Serial.println("Error leyendo el sensor DHT!");
    delay(2000);
    return;
  }

  // Imprimir datos del sensor
  Serial.print("Temperatura: ");
  Serial.print(t);
  Serial.println(" °C");

  // Construir cadena JSON
  String json = "{\"temperature\":" + String(t) + ",\"humidity\":" + String(h) + "}";
  Serial.println("Datos a enviar:");
  Serial.println(json);

  // Construir solicitud HTTP
  String request = "POST " + String(path) + " HTTP/1.1\r\n" +
                   "Host: " + String(host) + "\r\n" +
                   "Content-Type: application/json\r\n" +
                   "Content-Length: " + String(json.length()) + "\r\n" +
                   "Connection: close\r\n\r\n" +
                   json;

  // Enviar datos al servidor
  sendRequest(request);

  // Retardo entre lecturas
  delay(60000);
}

void configureWiFi() {
  Serial.println("Configurando SSID y contraseña a través del puerto serial:");

  while (!Serial.available()) {
    delay(100);
  }

  // Leer SSID desde el puerto serial
  Serial.print("SSID: ");
  int i = 0;
  while (Serial.available() && i < sizeof(ssid) - 1) {
    ssid[i] = Serial.read();
    i++;
    delay(10);
  }
  ssid[i] = '\0'; // Terminar con null character
  Serial.println(ssid);

  // Leer contraseña desde el puerto serial
  Serial.print("Contraseña: ");
  i = 0;
  while (Serial.available() && i < sizeof(password) - 1) {
    password[i] = Serial.read();
    i++;
    delay(10);
  }
  password[i] = '\0'; // Terminar con null character
  Serial.println(password);

  Serial.println("SSID y contraseña configurados correctamente.");
}

void connectToWiFi() {
  Serial.println("Conectando a WiFi...");
  WiFi.begin(ssid, password);

  // Esperar a que se establezca la conexión
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Intentando conectar a la red WiFi...");
  }

  Serial.println("Conectado a la red WiFi");
}

void sendRequest(String request) {
  if (client.connect(host, port)) {
    Serial.println("Enviando solicitud al servidor...");
    client.print(request);
    delay(10);
    client.stop();
    Serial.println("Solicitud enviada");
  } else {
    Serial.println("Error al conectar al servidor");
  }
}
