#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DNSServer.h>
#include <EEPROM.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Ticker.h>

// Pines de los sensores DS18B20
#define ONE_WIRE_BUS_1 4
#define ONE_WIRE_BUS_2 13
#define ONE_WIRE_BUS_3 12
// Pin para iniciar modo AP manualmente
#define AP_MODE_PIN 2

// Pines para los LEDs
#define LED_GREEN_PIN 14
#define LED_RED_PIN 15

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
DallasTemperature sensors1(&oneWire1);

// Configuración del AP
const char* apSSID = "MasterRef_WSD1ESP82660002";
const char* apPassword = "masterref"; // Opcional: Agrega una contraseña al AP

// Variables de tiempo
unsigned long lastCommandTime = 0;

// Watchdog
Ticker watchdog;

void resetModule() {
    ESP.restart();
}

void setup() {
    Serial.begin(115200);
    sensors1.begin();

    pinMode(AP_MODE_PIN, INPUT_PULLUP);
    pinMode(ONE_WIRE_BUS_2, INPUT);
    pinMode(ONE_WIRE_BUS_3, INPUT);
    
    pinMode(LED_GREEN_PIN, OUTPUT);
    pinMode(LED_RED_PIN, OUTPUT);

    // Inicializar EEPROM
    EEPROM.begin(512);
    
    readCredentials();
    
    if (strcmp(ssid, "default_ssid") != 0) {
        connectToWiFi();
    } else {
        Serial.println("No se encontraron credenciales. Iniciando modo AP...");
        startAPMode();
        digitalWrite(LED_GREEN_PIN, LOW);
        digitalWrite(LED_RED_PIN, HIGH);
    }

    // Iniciar watchdog
    watchdog.attach(300, resetModule);
}

void loop() {
    // Reiniciar el watchdog
    watchdog.detach();
    watchdog.attach(300, resetModule);

    if (digitalRead(AP_MODE_PIN) == LOW) {
        Serial.println("Botón presionado, limpiando credenciales y reiniciando...");
        clearCredentials();
        ESP.restart();
        return;
    }

    dnsServer.processNextRequest();
    server.handleClient();
    
    if (strcmp(ssid, "default_ssid") != 0) {
        if (WiFi.status() != WL_CONNECTED) {
            digitalWrite(LED_GREEN_PIN, LOW);
            digitalWrite(LED_RED_PIN, HIGH);
            Serial.println("WiFi desconectado. Intentando reconectar...");
            connectToWiFi();
        } else {
            if (millis() - lastCommandTime > 60000) {
                lastCommandTime = millis();
                readSensors();
            }
        }
    }
}

void connectToWiFi() {
    Serial.print("Conectando a ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);
    unsigned long startAttemptTime = millis();

    while (WiFi.status() != WL_CONNECTED) {
        digitalWrite(LED_GREEN_PIN, LOW);
        digitalWrite(LED_RED_PIN, HIGH);
        if (digitalRead(AP_MODE_PIN) == LOW) {
            Serial.println("Botón presionado, iniciando modo AP...");
            clearCredentials();
            startAPMode();
            return;
        }

        delay(1000);
        Serial.print(".");

        if (millis() - startAttemptTime > 30000) {
            Serial.println("\nFalló la conexión WiFi. Iniciando modo AP...");
            startAPMode();
            return;
        }
    }

    Serial.println("");
    Serial.println("WiFi conectado");
    Serial.println("Dirección IP: ");
    Serial.println(WiFi.localIP());

    digitalWrite(LED_GREEN_PIN, HIGH);
    digitalWrite(LED_RED_PIN, LOW);
    
    readSensors();
}

void readSensors() {
    sensors1.requestTemperatures();
    float t1 = sensors1.getTempCByIndex(0);
    int puerta = 0;
    int compresor = 0;
    bool t1Failed = (t1 == DEVICE_DISCONNECTED_C);

    if (t1Failed) {
        Serial.println("Error al leer el sensor DS18B20 1!");
    } else {
        Serial.print("Temperatura sensor 1: ");
        Serial.print(t1);
        Serial.println(" *C");
    }

    int sensorState = digitalRead(ONE_WIRE_BUS_2);
    if (sensorState == HIGH) {
        Serial.println("Puerta cerrada");
        puerta = 0;
    } else {
        Serial.println("Puerta abierta");
        puerta = 1;
    }
    
    int sensorState1 = digitalRead(ONE_WIRE_BUS_3);
    if (sensorState1 == HIGH) {
        Serial.println("Compresor Prendido");
        compresor = 1;
    } else {
        Serial.println("Compresor apagado");
        compresor = 0;
    }

    if (!t1Failed) {
        String json1 = "{\"temperature\":" + String(t1) + ", \"placa\":2, \"puerto\":1, \"puerta_status\":" + String(puerta) + ", \"compresor_status\":" + String(compresor) + "}";
        sendData(json1);
    }
}

void sendData(String json) {
    String request = "POST " + String(path) + " HTTP/1.1\r\n" +
                    "Host: " + String(host) + "\r\n" +
                    "Content-Type: application/json\r\n" +
                    "Content-Length: " + String(json.length()) + "\r\n" +
                    "Connection: close\r\n\r\n" +
                    json;

    Serial.println("Enviando datos al servidor:");
    Serial.println(request);

    if (client.connect(host, port)) {
        client.print(request);
    } else {
        Serial.println("Conexión fallida");
    }

    while (client.connected() && !client.available()) {
        delay(100);
    }

    while (client.available()) {
        String line = client.readStringUntil('\r');
        Serial.print(line);
    }

    client.stop();
}

void readCredentials() {
    Serial.println("Leyendo credenciales de EEPROM...");
    
    for (int i = 0; i < 32; i++) {
        ssid[i] = EEPROM.read(i);
    }
    for (int i = 0; i < 32; i++) {
        password[i] = EEPROM.read(32 + i);
    }

    ssid[31] = '\0';
    password[31] = '\0';

    Serial.print("SSID leído: ");
    Serial.println(ssid);
    Serial.print("Contraseña leída: ");
    Serial.println(password);
}

void writeCredentials() {
    Serial.println("Escribiendo credenciales en EEPROM...");
    
    for (int i = 0; i < 32; i++) {
        EEPROM.write(i, ssid[i]);
    }
    for (int i = 0; i < 32; i++) {
        EEPROM.write(32 + i, password[i]);
    }

    EEPROM.commit();

    Serial.println("Credenciales escritas en EEPROM");
}

void clearCredentials() {
    Serial.println("Limpiando credenciales de EEPROM...");
    
    for (int i = 0; i < 64; i++) {
        EEPROM.write(i, 0);
    }

    EEPROM.commit();

    strcpy(ssid, "default_ssid");
    strcpy(password, "default_password");

    Serial.println("Credenciales limpiadas");
}

void startAPMode() {
    Serial.println("Iniciando Punto de Acceso...");
    WiFi.softAP(apSSID, apPassword);
    delay(1000);
    IPAddress myIP = WiFi.softAPIP();
    Serial.print("Dirección IP del AP: ");
    Serial.println(myIP);
    dnsServer.start(53, "*", myIP);

    server.on("/", HTTP_GET, handleRoot);
    server.onNotFound([]() {
        server.sendHeader("Location", "/", true);
        server.send(302, "text/plain", "");
    });

    server.on("/config", HTTP_POST, handleConfig);
    server.begin();

    Serial.println("Modo AP iniciado. Conéctate a 'MasterRef_Sandbox' para configurar WiFi.");
}

void handleConfig() {
    if (server.hasArg("ssid") && server.hasArg("password")) {
        String newSSID = server.arg("ssid");
        String newPassword = server.arg("password");

        newSSID.trim();
        newPassword.trim();

        strncpy(ssid, newSSID.c_str(), sizeof(ssid) - 1);
        strncpy(password, newPassword.c_str(), sizeof(password) - 1);
        ssid[sizeof(ssid) - 1] = '\0';
        password[sizeof(password) - 1] = '\0';

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
    Serial.print("Redes encontradas: ");
    Serial.println(n);
    if (n == 0) {
        ssidList += "]";
    } else {
        for (int i = 0; i < n; i++) {
            if (i > 0) ssidList += ",";
            ssidList += "\"" + WiFi.SSID(i) + "\"";
            Serial.println("Red: " + WiFi.SSID(i));
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
        options = "<option value=''>No se encontraron redes</option>";
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
