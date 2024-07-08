import sys
import serial
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
import time

class SerialThread(QThread):
    serial_update = pyqtSignal(str)

    def __init__(self, port, baudrate, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self.serial_port = None
        self.running = False

    def run(self):
        try:
            self.serial_port = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            while self.running:
                if self.serial_port.in_waiting > 0:
                    try:
                        serial_data = self.serial_port.readline().decode('utf-8').strip()
                        self.serial_update.emit(serial_data)
                    except UnicodeDecodeError as e:
                        print(f"Error de decodificación: {e}")
        except serial.SerialException as e:
            print(f"Error de conexión serial: {e}")

    def stop(self):
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('wifi.ui', self)
        self.serial_thread = None
        self.pushButton.clicked.connect(self.update_wifi)
        self.setup_serial()

        # Crear un modelo de datos para la listView
        self.list_model = QStandardItemModel()
        self.listView.setModel(self.list_model)

    def setup_serial(self):
        self.serial_thread = SerialThread('/dev/ttyUSB0', 115200)
        self.serial_thread.serial_update.connect(self.update_listview)
        self.serial_thread.start()

    def update_wifi(self):
        ssid = self.lineEdit.text()
        password = self.lineEdit_2.text()
        if self.serial_thread and self.serial_thread.isRunning():
            self.serial_thread.serial_port.write(f"SSID:{ssid}\n".encode())
            time.sleep(1)
            self.serial_thread.serial_port.write(f"PASSWORD:{password}\n".encode())

    def update_listview(self, data):
        # Crear un nuevo elemento para la lista
        item = QStandardItem(data)
        # Agregar el elemento al modelo de datos
        self.list_model.appendRow(item)
        # Hacer scroll hasta el nuevo elemento
        self.listView.scrollToBottom()

    def closeEvent(self, event):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread.wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
