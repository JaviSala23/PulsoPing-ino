#ifndef WIFI_ES_H
#define WIFI_ES_H

#include <ESP8266WiFi.h>
#include <DHT.h>

// Definiciones de pines y tipo de sensor DHT
#define DHTPIN 4
#define DHTTYPE DHT22

extern const char* host;
extern const uint16_t port;
extern const char* path;
extern DHT dht;
extern char ssid[32];
extern char password[32];
extern WiFiClient client;

void setup();
void loop();
void readCredentials();
void writeCredentials();

#endif

