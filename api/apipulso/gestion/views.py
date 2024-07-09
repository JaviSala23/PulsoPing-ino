

# Create your views here.


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
            _, placa_id, puerto = file_path.split('/')[1].split('_')
            puerto = puerto.split('.')[0]

            # Leer datos del archivo
            with open(file_path, 'r') as f:
                lines = f.readlines()

            # Procesar cada línea de datos
            timestamps = []
            temperatures = []
            for line in lines:
                parts = line.strip().split(' - ')
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

            # Guardar la figura como imagen para mostrar en el template
            image_path = f"static/temperature_plots/{key}.png"
            plt.savefig(image_path)
            plots.append({'placa_id': placa_id, 'puerto': puerto, 'image_path': image_path})

        # Renderizar el template con los gráficos generados
        return render(request, 'temperature_graph.html', {'plots': plots})