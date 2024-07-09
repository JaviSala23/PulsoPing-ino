import os
from django.shortcuts import render
from django.views import View
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime
import glob

class TemperatureGraphView(View):
    def get(self, request):
        # Obtener la lista de archivos de texto guardados
        file_paths = glob.glob('readings/placa_*/puerto_*.txt')

        # Inicializar estructuras de datos para los gráficos
        data = {}
        for file_path in file_paths:
            # Obtener placa y puerto desde el nombre del archivo
            parts = os.path.basename(file_path).split('_')
            if len(parts) < 4:
                continue  # Saltar archivos que no cumplen con la estructura esperada
            
            placa_id = parts[1]
            puerto_parts = parts[3].split('.')
            if len(puerto_parts) < 1:
                continue  # Saltar archivos que no cumplen con la estructura esperada
            puerto = puerto_parts[0]

            # Leer datos del archivo
            with open(file_path, 'r') as f:
                lines = f.readlines()

            # Procesar cada línea de datos
            timestamps = []
            temperatures = []
            for line in lines:
                parts = line.strip().split(' - ')
                if len(parts) < 2:
                    continue  # Saltar líneas que no cumplen con la estructura esperada
                timestamp = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
                temperature = float(parts[1].split('°C')[0])
                timestamps.append(timestamp)
                temperatures.append(temperature)

            # Guardar datos en la estructura
            key = f"{placa_id}_{puerto}"
            data[key] = {'timestamps': timestamps, 'temperatures': temperatures}

        # Crear gráficos
        plots = []
        for key, values in data.items():
            placa_id, puerto = key.split('_')
            plt.figure()
            plt.plot(values['timestamps'], values['temperatures'], marker='o', linestyle='-', color='b')
            plt.title(f'Temperaturas - Placa {placa_id}, Puerto {puerto}')
            plt.xlabel('Tiempo')
            plt.ylabel('Temperatura (°C)')
            plt.xticks(rotation=45)
            plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))
            plt.tight_layout()

            # Convertir el gráfico a imagen en formato base64 y pasarla al template
            from io import BytesIO
            import base64

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            buffer.close()

            plots.append({'placa_id': placa_id, 'puerto': puerto, 'image_base64': image_base64})

            plt.close()  # Cerrar el gráfico para liberar memoria

        # Renderizar el template con los gráficos generados
        return render(request, 'graficos.html', {'plots': plots})
