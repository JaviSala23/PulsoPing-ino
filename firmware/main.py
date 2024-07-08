import subprocess
import os

def modificar_ino(ruta_ino, ssid, password):
    # Modifica el archivo .ino para configurar SSID y contraseña de WiFi
    with open(ruta_ino, 'r') as file:
        lines = file.readlines()

    with open(ruta_ino, 'w') as file:
        for line in lines:
            if '#define STASSID' in line:
                line = f'#define STASSID "{ssid}"\n'
            elif '#define STAPSK' in line:
                line = f'#define STAPSK "{password}"\n'
            file.write(line)

def compilar_sketch(ruta_ino, fqbn):
    # Compila el sketch utilizando Arduino CLI
    result = subprocess.run(['arduino-cli', 'compile', '--fqbn', fqbn, ruta_ino], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode == 0:
        print("Compilación exitosa.")
    else:
        print("Error en la compilación.")
        print(result.stderr)
        exit(1)

def upload_firmware(serial_port, firmware_path):
    # Carga el firmware en el ESP8266 utilizando Arduino CLI
    result = subprocess.run(['arduino-cli', 'upload', '-p', serial_port, '-b', 'esp8266:esp8266:generic', firmware_path], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode == 0:
        print("Firmware cargado exitosamente.")
    else:
        print("Error al cargar el firmware.")
        print(result.stderr)

if __name__ == '__main__':
    # Configuración inicial
    ruta_ino = 'senWi/senWi.ino'  # Ruta al archivo .ino
    ssid = '28428631'  # SSID de tu red WiFi
    password = 'FTTH-CVCA-belliceleste'  # Contraseña de tu red WiFi
    fqbn = 'esp8266:esp8266:generic'  # Configuración del hardware ESP8266
    serial_port = 'COM3'  # Puerto serial al que está conectado el ESP8266

    # Modificar el archivo .ino con los datos de red
    modificar_ino(ruta_ino, ssid, password)

    # Compilar el sketch
    compilar_sketch(ruta_ino, fqbn)

    # Generar la ruta del archivo .bin generado por la compilación
    firmware_path = os.path.splitext(ruta_ino)[0] + '.bin'

    # Cargar el firmware en el ESP8266
    upload_firmware(serial_port, firmware_path)
