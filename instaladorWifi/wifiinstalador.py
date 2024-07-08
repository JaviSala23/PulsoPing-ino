import serial
import time

def send_serial_commands(port, baudrate, ssid, password):
    # Configura la conexión serial
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)  # Espera para asegurar que la conexión esté establecida

    # Envía el comando SSID
    ssid_command = f"SSID:{ssid}\n"
    ser.write(ssid_command.encode())
    time.sleep(1)  # Espera un momento entre comandos

    # Envía el comando PASSWORD
    password_command = f"PASSWORD:{password}\n"
    ser.write(password_command.encode())
    time.sleep(1)  # Espera un momento para asegurar que el comando se envíe completamente

    ser.close()  # Cierra la conexión serial

if __name__ == "__main__":
    # Cambia estos valores según sea necesario
    serial_port = "/dev/ttyUSB0"  # Ejemplo de puerto en Ubuntu
    baud_rate = 115200
    ssid = "FTTH-CVCA-belliceleste"
    password = "28428631"

    send_serial_commands(serial_port, baud_rate, ssid, password)