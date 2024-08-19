#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DNSServer.h>
#include <FS.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// Pines de los sensores DS18B20
#define ONE_WIRE_BUS_1 4
#define ONE_WIRE_BUS_2 5

// Pin para iniciar modo AP manualmente
#define AP_MODE_PIN 2

// Pines para los LEDs
#define LED_GREEN_PIN 12
#define LED_RED_PIN 13

// Configuración de red WiFi predeterminada
char ssid[32] = "default_ssid";
char password[32] = "default_password";
const char* host = "mantistemp.com.ar";
const uint16_t port = 8000;
const char* path = "/sensor_readings/";

// Configuración del cliente WiFi
WiFiClient client;
ESP8266WebServer server(80);
DNSServer dnsServer;

// Configuración del sensor DS18B20
OneWire oneWire1(ONE_WIRE_BUS_1);
OneWire oneWire2(ONE_WIRE_BUS_2);
DallasTemperature sensors1(&oneWire1);
DallasTemperature sensors2(&oneWire2);

// Configuración del AP
const char* apSSID = "MasterRef_SandBox";
const char* apPassword = "masterref"; // Opcional: Agrega una contraseña al AP

// Variables de tiempo
unsigned long lastCommandTime = 0;

void setup() {
  Serial.begin(115200);
  sensors1.begin();
  sensors2.begin();

  pinMode(AP_MODE_PIN, INPUT_PULLUP);

   // Configurar pines de LEDs
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_RED_PIN, OUTPUT);

  if (SPIFFS.begin()) {
    Serial.println("File system mounted");
    readCredentials();
  } else {
    Serial.println("Failed to mount file system");
  }

  // Intentar conexión con las credenciales guardadas
  WiFi.begin(ssid, password);
  Serial.print("Connecting to ");
  Serial.println(ssid);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 10) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());

      // Encender LED verde
    digitalWrite(LED_GREEN_PIN, HIGH);
    digitalWrite(LED_RED_PIN, LOW);

    // Iniciar la lectura de sensores ahora que estamos conectados al WiFi
    readSensors();
  } else {
    Serial.println("Failed to connect to WiFi. Starting AP mode...");
    startAPMode();
       // Encender LED verde
    digitalWrite(LED_GREEN_PIN, LOW);
    digitalWrite(LED_RED_PIN, HIGH);
  }
}

void loop() {
  // Verificar si se presionó el botón para limpiar credenciales y reiniciar
  if (digitalRead(AP_MODE_PIN) == LOW) {
    Serial.println("Botón presionado, limpiando credenciales y reiniciando...");
    clearCredentials(); // Limpiar las credenciales
    ESP.restart(); // Reiniciar el ESP8266
    return; // Salir del loop para evitar ejecutar el resto del código después del reinicio
  }

  // Procesar solicitudes del portal cautivo
  dnsServer.processNextRequest();
  server.handleClient();

  if (WiFi.status() == WL_CONNECTED) {
    // Leer sensores y enviar datos cada 60 segundos
    if (millis() - lastCommandTime > 60000) {
      lastCommandTime = millis();
      readSensors();
    }
  }
}

void readSensors() {
  // Leer temperatura de los sensores DS18B20
  sensors1.requestTemperatures();
  sensors2.requestTemperatures();

  float t1 = sensors1.getTempCByIndex(0);
  float t2 = sensors2.getTempCByIndex(0);

  // Verificar si falló la lectura
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

  // Enviar datos si las lecturas son válidas
  if (!t1Failed) {
    String json1 = "{\"temperature\":" + String(t1) + ", \"placa\":1, \"puerto\":1}";
    sendData(json1);
  }

  if (!t2Failed) {
    String json2 = "{\"temperature\":" + String(t2) + ", \"placa\":1, \"puerto\":2}";
    sendData(json2);
  }
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

  // Esperar respuesta del servidor
  while (client.connected() && !client.available()) {
    delay(100);
  }

  // Leer la respuesta del servidor
  while (client.available()) {
    String line = client.readStringUntil('\r');
    Serial.print(line);
  }

  client.stop(); // Cerrar la conexión
}

void readCredentials() {
  File file = SPIFFS.open("/credentials.txt", "r");
  if (!file) {
    Serial.println("Failed to open credentials file");
    return;
  }

  file.readBytesUntil('\n', ssid, sizeof(ssid));
  ssid[strcspn(ssid, "\r\n")] = 0;  // Eliminar caracteres de nueva línea
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

void clearCredentials() {
  if (SPIFFS.remove("/credentials.txt")) {
    Serial.println("Archivo de credenciales borrado");
  } else {
    Serial.println("No se pudo borrar el archivo de credenciales");
  }

  // Limpiar las credenciales de WiFi
  ssid[0] = '\0';
  password[0] = '\0';
}

void startAPMode() {
  Serial.println("Starting Access Point...");
  WiFi.softAP(apSSID, apPassword);  // Iniciar AP con SSID y contraseña

  delay(1000);  // Esperar un momento para que el AP se inicie

  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);

  dnsServer.start(53, "*", myIP);

  server.on("/", HTTP_GET, handleRoot);
  server.onNotFound([]() {
    server.sendHeader("Location", "/", true);
    server.send(302, "text/plain", "");
  });

  server.on("/config", HTTP_POST, handleConfig); // Ruta para manejar la configuración de WiFi
  server.begin();

  Serial.println("AP Mode Started. Connect to 'MasterRef_Sandbox' to configure WiFi.");
}

void handleConfig() {
  if (server.hasArg("ssid") && server.hasArg("password")) {
    String newSSID = server.arg("ssid");
    String newPassword = server.arg("password");

    newSSID.trim();
    newPassword.trim();

    newSSID.toCharArray(ssid, sizeof(ssid));
    newPassword.toCharArray(password, sizeof(password));

    writeCredentials();
    
    server.send(200, "text/html", "<html><body><h1>Configuración guardada. Reiniciando...</h1></body></html>");
    delay(2000);
    ESP.restart();
  } else {
    server.send(400, "text/html", "<html><body><h1>Error: Faltan parámetros</h1></body></html>");
  }
}

void handleRoot() {
  String ssidList = "[";
  int n = WiFi.scanNetworks();
  Serial.print("Found networks: ");
  Serial.println(n);
  if (n == 0) {
    ssidList += "]";
  } else {
    for (int i = 0; i < n; i++) {
      if (i > 0) ssidList += ",";
      ssidList += "\"" + WiFi.SSID(i) + "\"";
      Serial.println("Network: " + WiFi.SSID(i));
    }
    ssidList += "]";
  }
  String page = generateHTMLPage(ssidList);
  server.send(200, "text/html", page);
}

String generateHTMLPage(String ssidList) {
  // Generar las opciones del menú desplegable para SSID
  String options = "";
  if (ssidList != "[]") {
    // Convertir JSON array a opciones de <select>
    int start = 1; // Empezar después del primer corchete
    int end = ssidList.indexOf(']');
    while (start < end) {
      int comma = ssidList.indexOf(',', start);
      if (comma == -1 || comma > end) comma = end;

      String ssid = ssidList.substring(start, comma);
      ssid.replace("\"", ""); // Eliminar comillas innecesarias
      options += "<option value='" + ssid + "'>" + ssid + "</option>";

      start = comma + 1;
    }
  } else {
    options = "<option value=''>No networks found</option>";
  }

  return String("<!DOCTYPE html><html><head>"
         "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
         "<style>"
         "body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }"
         "h1 { color: #333; text-align: center; margin-top: 20px; }"
         "form { max-width: 600px; margin: 20px auto; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }"
         "label { display: block; margin-bottom: 10px; font-size: 18px; color: #555; }"
         "input[type='text'], input[type='password'], select { width: 100%; padding: 12px; font-size: 16px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }"
         "input[type='submit'] { padding: 12px; font-size: 16px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; width: 100%; }"
         "input[type='submit']:hover { background-color: #45a049; }"
         "</style>"
         "</head><body>"
         "<h1>Configuración de WiFi</h1>"
         "<form method='post' action='/config'>"
         "<label for='ssid'>Selecciona la red WiFi</label>"
         "<select id='ssid' name='ssid'>" + options + "</select>"
         "<label for='password'>Contraseña</label>"
         "<input type='password' id='password' name='password' required>"
         "<input type='submit' value='Guardar'>"
         "</form>"
         "</body></html>");
}