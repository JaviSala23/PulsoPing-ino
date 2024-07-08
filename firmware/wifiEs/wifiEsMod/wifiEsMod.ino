#include <ESP8266WiFi.h>
#include <DHT.h>
#include <FS.h>

#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

char ssid[32] = "default_ssid";
char password[32] = "default_password";
const char* host = "habitatonline.ar";
const uint16_t port = 801;
const char* path = "/sensor-readings/";

WiFiClient client;

unsigned long lastCommandTime = 0;  // Variable to track last command received time

void setup() {
  Serial.begin(115200);
  dht.begin();

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
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
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
   // Read temperature from AM2302 sensor
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Sensor reading and data transmission logic (unchanged)
  delay(2000);
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

delay(60000); // Delay to control the sensing and sending interval

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

