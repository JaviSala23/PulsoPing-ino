import os
import requests
from rest_framework import generics
from .models import SensorReading, MessageLog
from gestion.models import Cuenta_has_Artefacto
from .serializers import SensorReadingSerializer
from datetime import datetime, timedelta

class SensorReadingListCreate(generics.ListCreateAPIView):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer 

    def perform_create(self, serializer):
        # Guardar en un archivo de texto
        self.save_to_file(serializer.validated_data)

        # Obtener el último registro de la base de datos para el mismo puerto
        last_reading = SensorReading.objects.filter(puerto=serializer.validated_data['puerto']).order_by('timestamp').last()

        # Verificar si la variación de temperatura es al menos 0.5 grados para el mismo puerto
        if last_reading is None or abs(serializer.validated_data['temperature'] - last_reading.temperature) >= 0.5:
            serializer.save()
            self.check_temperature_and_notify(serializer.instance)

    def save_to_file(self, data):
        placa_id = data['placa'].id
        puerto = data['puerto']
        
        # Crear el directorio basado en el número de la placa si no existe
        directory = f"readings/placa_{placa_id}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Nombre del archivo basado en el puerto
        file_path = os.path.join(directory, f"puerto_{puerto}.txt")
        
        # Asegurar que el timestamp esté presente en los datos
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Guardar los datos en el archivo de texto
        with open(file_path, 'a') as f:
            f.write(f"{data['timestamp']} - {data['temperature']}°C - Placa: {data['placa']} - Puerto: {data['puerto']}\n")

    def check_temperature_and_notify(self, reading):
        # Obtener los rangos de temperatura de Cuenta_has_Artefacto
        cuenta_artefacto = Cuenta_has_Artefacto.objects.get(placa=reading.placa, puerto=reading.puerto)
        temp_min = cuenta_artefacto.temp_min
        temp_max = cuenta_artefacto.temp_max

        # Comprobar si la temperatura excede los límites
        if reading.temperature < temp_min or reading.temperature > temp_max:
            self.send_alert(reading, temp_min, temp_max)
        else:
            self.send_stable(reading)

    def send_alert(self, reading, temp_min, temp_max):
        # Verificar el último mensaje enviado para esta placa y puerto
        last_message = MessageLog.objects.filter(placa=reading.placa, puerto=reading.puerto, message_type="ALERT").last()

        if last_message is None or datetime.now() - last_message.timestamp >= timedelta(minutes=30):
            # Enviar un mensaje de alerta por Telegram
            self.send_telegram_message(f"Alerta: La temperatura {reading.temperature}°C excede los límites ({temp_min}°C - {temp_max}°C) para Placa: {reading.placa.id}, Puerto: {reading.puerto}")
            MessageLog.objects.create(placa=reading.placa, puerto=reading.puerto, message_type="ALERT")

    def send_stable(self, reading):
        # Verificar el último mensaje enviado para esta placa y puerto
        last_alert = MessageLog.objects.filter(placa=reading.placa, puerto=reading.puerto, message_type="ALERT").last()
        last_stable = MessageLog.objects.filter(placa=reading.placa, puerto=reading.puerto, message_type="STABLE").last()

        if last_alert and (last_stable is None or last_alert.timestamp > last_stable.timestamp):
            # Enviar un mensaje indicando que la temperatura ha vuelto a los límites normales
            self.send_telegram_message(f"Estable: La temperatura ha vuelto a los límites normales para Placa: {reading.placa.id}, Puerto: {reading.puerto}")
            MessageLog.objects.create(placa=reading.placa, puerto=reading.puerto, message_type="STABLE")

    def send_telegram_message(self, message):
        # Aquí debes implementar la lógica para enviar el mensaje por Telegram
        telegram_token = '7157402657:AAHIiCK42UKAslXGH0SU0HDpyBwEjjo0xo4'
        chat_id = '6476665770'
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        params = {
            'chat_id': chat_id,
            'text': message
        }
        response = requests.get(url, params=params)
        return response.json()

class SensorReadingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
