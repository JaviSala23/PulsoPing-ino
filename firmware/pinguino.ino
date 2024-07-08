#include <ESP8266WiFi.h>
#include <WiFiClient.h>

const char* ssid = "nombre_de_tu_red_wifi";
const char* password = "contraseña_de_tu_red_wifi";
const char* serverUrl = "http://url_de_tu_sensor";

void setup() {
  Serial.begin(115200);

  // Conexión a la red WiFi
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando a WiFi...");
  }

  Serial.println("Conectado a la red WiFi");
}

void loop() {
  // Ejemplo de datos a enviar
  String datos = "temperatura=25"; // Ejemplo de datos
  
  // Crear un cliente WiFi
  WiFiClient client;
  
  // Hacer la solicitud POST
  if (client.connect(serverUrl, 80)) {
    client.println("POST /ruta_del_sensor HTTP/1.1");
    client.println("Host: url_de_tu_sensor");
    client.println("Content-Type: application/x-www-form-urlencoded");
    client.print("Content-Length: ");
    client.println(datos.length());
    client.println();
    client.print(datos);
    client.println();
  } else {
    Serial.println("Error al conectar con el servidor");
  }

  delay(5000); // Esperar un poco antes de enviar la siguiente solicitud
}
