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
    print(f"Archivos encontrados: {file_paths}")  # Verifica qué archivos se están encontrando

    # Inicializar una lista para almacenar los datos
    data = []

    for file_path in file_paths:
        print(f"Procesando archivo: {file_path}")
        # Obtener placa y puerto desde el nombre del archivo
        parts = os.path.basename(file_path).split('_')
        if len(parts) < 4:
            print(f"Nombre de archivo no válido: {file_path}")
            continue  # Saltar archivos que no cumplen con la estructura esperada

        try:
            # Leer datos del archivo
            with open(file_path, 'r') as f:
                lines = f.readlines()
            print(f"Líneas leídas: {lines}")
        except Exception as e:
            print(f"Error leyendo archivo {file_path}: {e}")
            continue

        for line in lines:
            print(f"Procesando línea: {line}")
            parts = line.strip().split(',')
            if len(parts) < 4:
                print(f"Línea no válida: {line}")
                continue  # Saltar líneas que no cumplen con la estructura esperada

            try:
                timestamp = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
                temperature = float(parts[1])
                placa_id = parts[2]
                puerto = parts[3]
                data.append((timestamp, temperature, placa_id, puerto))
            except Exception as e:
                print(f"Error procesando línea {line}: {e}")
                continue

    # Convertir los datos en un DataFrame de pandas
    if not data:
        return HttpResponse("No se encontraron datos válidos en los archivos.", content_type="text/plain")

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
