import subprocess

def ejecutar_comando(comando):
    # Función para ejecutar un comando en la línea de comandos
    subprocess.run(comando, shell=True, check=True)

def instalar_esp8266():
    # Agregar el URL del paquete ESP8266
    ejecutar_comando("arduino-cli core update-index --add-url http://arduino.esp8266.com/stable/package_esp8266com_index.json")
    
    # Actualizar los índices de los paquetes
    ejecutar_comando("arduino-cli core update-index")
    
    # Instalar el núcleo ESP8266
    ejecutar_comando("arduino-cli core install esp8266:esp8266")

def instalar_dht_library():
    # Instalar la biblioteca del sensor DHT
    ejecutar_comando("arduino-cli lib install DHT sensor")

def main():
    try:
        # Instalar ESP8266
        instalar_esp8266()
        
        # Instalar biblioteca del sensor DHT
        instalar_dht_library()
        
        print("Instalación completada con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e}")

if __name__ == "__main__":
    main()
