#include <ESP8266WiFi.h>
#include "DHT.h"

#ifndef STASSID
#define STASSID "FTTH-CVCA-belliceleste"
#define STAPSK "28428631"
#endif

const char* ssid = STASSID;
const char* password = STAPSK;

const char* host = "habitatonline.ar";
const uint16_t port = 8000;
const char* path = "/listaArticulosVendedores/0";

#define DHTPIN D2     // GPIO2 (D4 on NodeMCU)
#define DHTTYPE DHT22 // AM2302 is DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  static bool wait = false;

  Serial.print("connecting to ");
  Serial.print(host);
  Serial.print(':');
  Serial.println(port);

  // Read temperature from AM2302 sensor
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    delay(2000);
    return;
  }

  Serial.print("Temperature: ");
  Serial.print(t);
  Serial.println(" *C");

  WiFiClient client;
  if (!client.connect(host, port)) {
    Serial.println("connection failed");
    delay(5000);
    return;
  }

  String request = String("GET ") + path + "?temp=" + String(t) + " HTTP/1.1\r\n" +
                   "Host: " + host + "\r\n" +
                   "Connection: close\r\n\r\n";

  Serial.println("sending data to server");
  if (client.connected()) {
    client.print(request);
  }

  unsigned long timeout = millis();
  while (client.available() == 0) {
    if (millis() - timeout > 5000) {
      Serial.println(">>> Client Timeout !");
      client.stop();
      delay(60000);
      return;
    }
  }

  Serial.println("receiving from remote server");
  while (client.available()) {
    char ch = static_cast<char>(client.read());
    Serial.print(ch);
  }

  Serial.println();
  Serial.println("closing connection");
  client.stop();

  if (wait) {
    delay(300000);  // execute once every 5 minutes, don't flood remote service
  }
  wait = true;
}

