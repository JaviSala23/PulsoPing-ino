import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from .models import Cuenta_has_Artefacto

def TemperatureGraphView(request, cuenta, puerto):
    try:
        # Obtener el objeto Cuenta_has_Artefacto correspondiente
        artefacto1 = Cuenta_has_Artefacto.objects.get(cuenta=cuenta, puerto=puerto)
    except Cuenta_has_Artefacto.DoesNotExist:
        return HttpResponse("No se encontró el artefacto especificado.", content_type="text/plain")
    
    data = []
    
    try:
        # Limpiar la URL para evitar caracteres de nueva línea
        url_clean = artefacto1.url.strip()

        # Leer datos del archivo
        with open(url_clean, 'r') as f:
            lines = f.readlines()
        print(f"Líneas leídas: {lines}")
    except Exception as e:
        print(f"Error leyendo archivo {url_clean}: {e}")
        return HttpResponse(f"Error leyendo archivo {url_clean}: {e}", content_type="text/plain")

    for line in lines:
        print(f"Procesando línea: {line}")
        parts = line.strip().split(',')
        if len(parts) < 2:
            print(f"Línea no válida: {line}")
            continue  # Saltar líneas que no cumplen con la estructura esperada

        try:
            timestamp = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
            temperature = float(parts[1])
            data.append((timestamp, temperature))
        except Exception as e:
            print(f"Error procesando línea {line}: {e}")
            continue

    # Convertir los datos en un DataFrame de pandas
    if not data:
        return HttpResponse("No se encontraron datos válidos en los archivos.", content_type="text/plain")

    df = pd.DataFrame(data, columns=['timestamp', 'temperature'])
    print(df)

    # Crear un gráfico con matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df['timestamp'], df['temperature'], label=f'Cuenta: {artefacto1.cuenta.nombre_cuenta}, Puerto {puerto}, {artefacto1.artefacto.descripcion}')
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
