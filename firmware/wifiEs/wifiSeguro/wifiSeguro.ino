#include <ESP8266WiFi.h>
#include <FS.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS_1 4 // Pin for the first DS18B20 sensor
#define ONE_WIRE_BUS_2 5 // Pin for the second DS18B20 sensor

OneWire oneWire1(ONE_WIRE_BUS_1);
OneWire oneWire2(ONE_WIRE_BUS_2);

DallasTemperature sensors1(&oneWire1);
DallasTemperature sensors2(&oneWire2);

char ssid[32] = "default_ssid";
char password[32] = "default_password";
const char* host = "mantistemp.com.ar";
const uint16_t port = 443;
const char* path = "/sensor_readings/";

WiFiClientSecure client;

unsigned long lastCommandTime = 0;  // Variable to track last command received time

void setup() {
  Serial.begin(115200);
  sensors1.begin();
  sensors2.begin();

  if (SPIFFS.begin()) {
    Serial.println("File system mounted");
    readCredentials();
  } else {
    Serial.println("Failed to mount file system");
  }

  // Crear archivo de credenciales si no existe
  if (!SPIFFS.exists("/credentials.txt")) {
    Serial.println("Creating credentials file");
    File file = SPIFFS.open("/credentials.txt", "w");
    if (file) {
      file.println("default_ssid");
      file.println("default_password");
      file.close();
      Serial.println("Credentials file created");
    } else {
      Serial.println("Failed to create credentials file");
    }
  }

  // Leer las credenciales
  readCredentials();

  // Attempt connection with default credentials first
  WiFi.begin(ssid, password);
  Serial.print("Connecting to ");
  Serial.println(ssid);

  // Esperar hasta que se establezca la conexión WiFi
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 5) {
    delay(500);
    Serial.print(".");
    retries++;
  }
  Serial.println("");
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Failed to connect to WiFi");
  }
}

void loop() {
  // Check for new credentials every 2 seconds
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    lastCommandTime = millis();  // Reset timer

    Serial.print("Comando recibido: ");
    Serial.println(command);

    if (command.startsWith("SSID:")) {
      command.substring(5).toCharArray(ssid, sizeof(ssid));
      writeCredentials();
      WiFi.disconnect();  // Disconnect to attempt reconnection with new credentials
    } else if (command.startsWith("PASSWORD:")) {
      command.substring(9).toCharArray(password, sizeof(password));
      writeCredentials();
    } else {
      Serial.println("Comando no reconocido");
    }
  }
  
  // Read temperature from DS18B20 sensors
  sensors1.requestTemperatures();
  sensors2.requestTemperatures();
  
  float t1 = sensors1.getTempCByIndex(0);
  float t2 = sensors2.getTempCByIndex(0);
  
  // Check if any reads failed
  bool t1Failed = (t1 == DEVICE_DISCONNECTED_C);
  bool t2Failed = (t2 == DEVICE_DISCONNECTED_C);

  if (t1Failed) {
    Serial.println("Failed to read from DS18B20 sensor 1!");
  } else {
    Serial.print("Temperature sensor 1: ");
    Serial.print(t1);
    Serial.println(" *C");
  }

  if (t2Failed) {
    Serial.println("Failed to read from DS18B20 sensor 2!");
  } else {
    Serial.print("Temperature sensor 2: ");
    Serial.print(t2);
    Serial.println(" *C");
  }

  // Build JSON payload only if the sensor readings are valid
  if (!t1Failed) {
    String json1 = "{\"temperature\":" + String(t1) + ", \"placa\":1, \"puerto\":1}";
    sendData(json1);
  }

  if (!t2Failed) {
    String json2 = "{\"temperature\":" + String(t2) + ", \"placa\":1, \"puerto\":2}";
    sendData(json2);
  }

  delay(60000); // Delay to control the sensing and sending interval
}

void sendData(String json) {
  String request = "POST " + String(path) + " HTTP/1.1\r\n" +
                   "Host: " + String(host) + "\r\n" +
                   "Content-Type: application/json\r\n" +
                   "Content-Length: " + String(json.length()) + "\r\n" +
                   "Connection: close\r\n\r\n" +
                   json;

  Serial.println("Sending data to server:");
  Serial.println(request);

  if (client.connect(host, port)) {
    client.print(request);
  } else {
    Serial.println("Connection failed");
  }

  // Wait for response from server
  while (client.connected() && !client.available()) {
    delay(100); // Wait for data
  }

  // Read response from server
  while (client.available()) {
    String line = client.readStringUntil('\r');
    Serial.print(line);
  }

  client.stop(); // Close connection
}

void readCredentials() {
  File file = SPIFFS.open("/credentials.txt", "r");
  if (!file) {
    Serial.println("Failed to open credentials file");
    return;
  }

  file.readBytesUntil('\n', ssid, sizeof(ssid));
  ssid[strcspn(ssid, "\r\n")] = 0;  // Remove newline characters
  file.readBytesUntil('\n', password, sizeof(password));
  password[strcspn(password, "\r\n")] = 0;
  file.close();

  Serial.print("SSID cargado desde el archivo: ");
  Serial.println(ssid);
  Serial.print("Contraseña cargada desde el archivo: ");
  Serial.println(password);
}

void writeCredentials() {
  File file = SPIFFS.open("/credentials.txt", "w");
  if (!file) {
    Serial.println("Failed to open credentials file for writing");
    return;
  }

  file.println(ssid);
  file.println(password);
  file.close();

  Serial.println("Credenciales actualizadas y escritas en el archivo");
}