import os
import glob
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render
from django.http import HttpResponse


def TemperatureGraphView(request):
    # Obtener la lista de archivos de texto guardados
    file_paths = glob.glob('/home/sensor/PulsoPing-ino/api/apipulso/readings/placa_*/puerto_*.txt')
    print(file_paths)  # Verifica qué archivos se están encontrando

    # Inicializar una lista para almacenar los datos
    data = []

    for file_path in file_paths:
        print(file_path)
        # Obtener placa y puerto desde el nombre del archivo
        parts = os.path.basename(file_path).split('_')
        if len(parts) < 4:
            continue  # Saltar archivos que no cumplen con la estructura esperada
        print(parts)
        # Leer datos del archivo
        with open(file_path, 'r') as f:
            lines = f.readlines()
            print(lines)

        for line in lines:
            print(line)
            parts = line.strip().split(',')

            if len(parts) < 4:
                continue  # Saltar líneas que no cumplen con la estructura esperada


            timestamp = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
            temperature = float(parts[1])
            placa_id = parts[2]
            puerto = parts[3]
            data.append((timestamp, temperature, placa_id, puerto))

    # Convertir los datos en un DataFrame de pandas
    df = pd.DataFrame(data, columns=['timestamp', 'temperature', 'placa_id', 'puerto'])
    print(df)
    # Crear un gráfico con matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))
    for key, grp in df.groupby(['placa_id', 'puerto']):
        ax.plot(grp['timestamp'], grp['temperature'], label=f'Placa {key[0]} Puerto {key[1]}')

    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Temperature')
    ax.legend(loc='best')
    plt.xticks(rotation=45)

    # Guardar el gráfico en un objeto BytesIO
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Codificar la imagen en base64 para poder insertarla en la plantilla
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # Renderizar la plantilla con el gráfico
    return render(request, 'graficos.html', {'graph': image_base64})
