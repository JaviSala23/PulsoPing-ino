#include <ESP8266WiFi.h>
#include <DHT.h>

#ifndef STASSID
#define STASSID "default_ssid"  // SSID de red WiFi por defecto
#define STAPSK  "default_pass"  // Contraseña de red WiFi por defecto
#endif

const char* ssid_wifi = STASSID;
const char* pass = STAPSK;

const char* host_wifi = "habitatonline.ar";
const uint16_t port_wifi = 801;
const char* path_wifi = "/sensor-readings/";

#define DHTPIN 4    // Pin donde está conectado el sensor DHT
#define DHTTYPE DHT22 // Tipo de sensor DHT (DHT22)

DHT dht(DHTPIN, DHTTYPE);
WiFiClient client;

void setup() {
  Serial.begin(115200);
  dht.begin();

  Serial.println();
  Serial.println();
  Serial.print("Conectando a ");
  Serial.println(ssid_wifi_wifi);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid_wifi, pass);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi conectado");
  Serial.println("Dirección IP: ");
  Serial.println(WiFi.localIP());

  Serial.print("Conectando a ");
  Serial.print(host_wifi);
  Serial.print(':');
  Serial.println(port_wifi);

  if (!client.connect(host_wifi, port_wifi)) {
    Serial.println("Falló la conexión");
    delay(5000);
    return;
  }
}

void loop() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println("Error al leer el sensor DHT!");
    delay(2000);
    return;
  }

  String json = "{\"temperature\":" + String(t) + ",\"humidity\":" + String(h) + "}";
  Serial.println("Datos a enviar:");
  Serial.println(json);

  String request = "POST " + String(path_wifi) + " HTTP/1.1\r\n" +
                   "Host: " + String(host) + "\r\n" +
                   "Content-Type: application/json\r\n" +
                   "Content-Length: " + String(json.length()) + "\r\n" +
                   "Connection: close\r\n\r\n" +
                   json;

  Serial.println("Enviando solicitud al servidor...");
  if (client.connected()) {
    client.print(request);
  } else {
    Serial.println("Conexión perdida, reconectando...");
    if (!client.connect(host_wifi, port_wifi)) {
      Serial.println("Reconexión fallida");
      delay(5000);
      return;
    }
    client.print(request);
  }

  while (client.connected()) {
    String line = client.readStringUntil('\n');
    if (line == "\r") {
      break;
    }
  }

  delay(60000); // Intervalo de 60 segundos entre lecturas
}

