import subprocess
import serial
import time

def modificar_ino(ruta_ino, ssid, password):
    with open(ruta_ino, 'r') as file:
        lines = file.readlines()

    with open(ruta_ino, 'w') as file:
        for line in lines:
            if '#define STASSID' in line:
                line = f'#define STASSID "{ssid}"\n'
            if '#define STAPSK' in line:
                line = f'#define STAPSK "{password}"\n'
            file.write(line)

def compilar_sketch(ruta_ino, fqbn):
    result = subprocess.run(['arduino-cli', 'compile', '--fqbn', fqbn, ruta_ino], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode == 0:
        print("Compilación exitosa.")
    else:
        print("Error en la compilación.")
        print(result.stderr)
        exit(1)

def reset_arduino(serial_port, baud_rate):
    ser = serial.Serial(serial_port, baud_rate)
    ser.setDTR(False)
    time.sleep(1)
    ser.setDTR(True)
    ser.close()

def upload_firmware(serial_port, baud_rate, firmware_path):
    avrdude_command = [
        'avrdude',
        '-v',
        '-patmega328p',  # Cambia esto según tu microcontrolador
        '-carduino',
        f'-P{serial_port}',
        f'-b{baud_rate}',
        '-D',
        f'-Uflash:w:{firmware_path}:i'
    ]
    reset_arduino(serial_port, baud_rate)
    result = subprocess.run(avrdude_command, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode == 0:
        print("Firmware cargado exitosamente.")
    else:
        print("Error al cargar el firmware.")
        print(result.stderr)

if __name__ == '__main__':
    ruta_ino = 'senWi/senWi.ino'  # Cambia esto por la ruta real a tu archivo .ino
    ssid = '28428631'  # Cambia esto por el SSID real de tu red WiFi
    password = 'FTTH-CVCA-belliceleste'  # Cambia esto por la contraseña real de tu red WiFi
    fqbn = 'arduino:avr:uno'  # Cambia esto según tu placa Arduino
    serial_port = '/dev/ttyUSB0'  # Cambia esto al puerto correspondiente
    baud_rate = 115200

    modificar_ino(ruta_ino, ssid, password)
    compilar_sketch(ruta_ino, fqbn)

    firmware_path = ruta_ino.replace('.ino', '.ino.hex')
    upload_firmware(serial_port, baud_rate, firmware_path)
