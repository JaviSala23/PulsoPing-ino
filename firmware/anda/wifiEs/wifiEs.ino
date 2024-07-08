#include <ESP8266WiFi.h>
#include <DHT.h>

#ifndef STASSID
#define STASSID "FTTH-CVCA-belliceleste"
#define STAPSK "28428631"
#endif

const char* ssid = STASSID;
const char* password = STAPSK;

const char* host = "habitatonline.ar";
const uint16_t port = 801;
const char* path = "/sensor-readings/";
#define DHTPIN 4    // Define the pin where the data pin of the AM2302 is connected
#define DHTTYPE DHT22 // Define the type of DHT sensor (AM2302 is DHT22)

DHT dht(DHTPIN, DHTTYPE);

WiFiClient client;

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

  Serial.print("connecting to ");
  Serial.print(host);
  Serial.print(':');
  Serial.println(port);

  // Connect to server
  if (!client.connect(host, port)) {
    Serial.println("connection failed");
    delay(5000);
    return;
  }
}

void loop() {
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

  String json = "{\"temperature\":" + String(t) + "}";
  Serial.println("json");
  Serial.println(json);
  String request = String("POST ") + path + " HTTP/1.1\r\n" +
                   "Host: " + host + "\r\n" +
                   "Content-Type: application/json\r\n" +
                   "Content-Length: " + String(json.length()) + "\r\n" +
                   "Connection: keep-alive\r\n\r\n" +
                   json;

  Serial.println("sending data to server");
  if (client.connected()) {
    client.print(request);
  } else {
    Serial.println("connection lost, reconnecting...");
    if (!client.connect(host, port)) {
      Serial.println("reconnection failed");
      delay(5000);
      return;
    }
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
  Serial.println("keeping connection open");

  delay(60000); // Delay to control the sensing and sending interval, e.g., 60 seconds
}

