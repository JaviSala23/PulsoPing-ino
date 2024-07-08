import serial
import time

# Configuración del puerto serial
serial_port = 'COM3'  # Ajusta el puerto serial según tu configuración
baud_rate = 115200
timeout = 1  # Tiempo de espera para la comunicación serial

# Función para enviar comandos al ESP8266
def send_command(command):
    with serial.Serial(serial_port, baud_rate, timeout=timeout) as ser:
        ser.write(command.encode())
        time.sleep(0.1)  # Espera breve para asegurar que se envíe completamente
        response = ser.read_all().decode().strip()
        return response

# Función para configurar el SSID y la contraseña
def configure_wifi(ssid, password):
    response = send_command(f"setSSID={ssid}\n")
    print("Respuesta SSID:", response)
    response = send_command(f"setPass={password}\n")
    print("Respuesta contraseña:", response)

if __name__ == "__main__":
    ssid = "tuSSID"  # Reemplaza con tu SSID
    password = "tuContraseña"  # Reemplaza con tu contraseña

    configure_wifi(ssid, password)