import os
from rest_framework import generics
from .models import SensorReading
from .serializers import SensorReadingSerializer
from datetime import datetime

class SensorReadingListCreate(generics.ListCreateAPIView):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer 

    def perform_create(self, serializer):
        # Guardar en un archivo de texto
        self.save_to_file(serializer.validated_data)

        # Obtener el último registro de la base de datos
        last_reading = SensorReading.objects.order_by('timestamp').last()

        # Verificar si la variación de temperatura es al menos 0.5 grados
        if last_reading is None or abs(serializer.validated_data['temperature'] - last_reading.temperature) >= 0.5:
            serializer.save()

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

class SensorReadingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
