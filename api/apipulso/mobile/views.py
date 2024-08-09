from django.shortcuts import render,redirect
from gestion.models import Cuenta_has_Artefacto
from gestion.views import obtener_ultimo_registro
from django.http import JsonResponse
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import mpld3
from datetime import datetime
from django.utils.dateparse import parse_datetime
import os
from django.template.loader import render_to_string
from matplotlib.dates import DateFormatter
from mpld3 import fig_to_html, plugins
import json
from datetime import datetime, timedelta
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import PermissionDenied

def login_view(request):
    error_message = request.GET.get('error', None)
    form = AuthenticationForm()
    context = {
        'form': form,
        'error_message': error_message
    }
    return render(request, 'mobile/login.html', context)

def authenticate_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()  # Obtiene el usuario autenticado
            auth_login(request, user)  # Autentica al usuario y establece la sesión
            return redirect('panelMobile')  # Redirige a una vista protegida
        else:
            return redirect('login_mobile')  # Redirige al formulario de inicio de sesión en caso de error
    else:
        return redirect('login_mobile') 

def panel_view(request):
    print("anda")
     # Filtrar las relaciones según el grupo del usuario
    if request.user.groups.filter(name='Clientes').exists():
        relaciones = Cuenta_has_Artefacto.objects.filter(cuenta__usuario=request.user)  # Ajusta este filtro según tu modelo
        print("cliente")
        print(relaciones)
    else:
        relaciones = Cuenta_has_Artefacto.objects.all()  # No mostrar nada si no es del grupo "Clientes"
        print("admin")
        print(relaciones)

    

    # Lista para almacenar relaciones junto con sus últimos registros de temperatura
    relaciones_actualizadas = []

    # Itera sobre las relaciones para obtener y agregar el último registro de temperatura
    for relacion in relaciones:
        archivo_path = relacion.url  # Ajusta esto según tu modelo y campo correspondiente
        print(archivo_path)
        try:
            ultimo_registro = obtener_ultimo_registro(archivo_path)
        except:
            ultimo_registro=0
        # Agrega un diccionario con la relación y el último registro de temperatura
        relaciones_actualizadas.append({
            'relacion': relacion,
            'ultimo_registro': ultimo_registro
        })
        print(relaciones_actualizadas)
    return render(request, 'mobile/panel.html', {'relaciones_actualizadas': relaciones_actualizadas})

def actualizar_relaciones_mobile(request):
    relaciones = Cuenta_has_Artefacto.objects.all()

    # Lista para almacenar relaciones junto con sus últimos registros de temperatura
    relaciones_actualizadas = []

    # Itera sobre las relaciones para obtener y agregar el último registro de temperatura
    for relacion in relaciones:
        archivo_path = relacion.url  # Ajusta esto según tu modelo y campo correspondiente
        ultimo_registro = obtener_ultimo_registro(archivo_path)

        # Convierte la relación a un formato serializable
        relacion_serializable = {
            'id':relacion.id,
            'cuenta': relacion.cuenta.nombre_cuenta,
            'artefacto': relacion.artefacto.descripcion,  # Ajusta esto según tus campos
            'puerto': relacion.puerto ,
            # Agrega otros campos relevantes de tu modelo
        }

        # Agrega un diccionario con la relación y el último registro de temperatura
        relaciones_actualizadas.append({
            'relacion': relacion_serializable,
            'ultimo_registro': ultimo_registro
        })

    # Renderizar solo el contenido de la ta
    
    return JsonResponse({'relaciones_actualizadas': relaciones_actualizadas})



# Diccionarios para traducir nombres de días y meses
DIAS_ESPANOL = {
    0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
    4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
}

MESES_ESPANOL = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

def translate_timestamp(timestamp):
    # Función para traducir el timestamp a español
    return timestamp.strftime('%d/%m %H:%M')

def TemperatureGraphView(request, id):
    try:
        # Obtener el objeto Cuenta_has_Artefacto correspondiente
        artefacto1 = Cuenta_has_Artefacto.objects.get(pk=id)
    except Cuenta_has_Artefacto.DoesNotExist:
        return HttpResponse("No se encontró el artefacto especificado.", content_type="text/plain")
    
    data = []
    
    try:
        # Limpiar la URL para evitar caracteres de nueva línea
        url_clean = artefacto1.url.strip()

        # Leer datos del archivo
        with open(url_clean, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        return HttpResponse(f"Error leyendo archivo {url_clean}: {e}", content_type="text/plain")

    for line in lines:
        parts = line.strip().split(',')
        if len(parts) < 2:
            continue

        try:
            timestamp = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
            temperature = float(parts[1])
            data.append((timestamp, temperature))
        except Exception as e:
            continue

    # Convertir los datos en un DataFrame de pandas
    if not data:
        return HttpResponse("No se encontraron datos válidos en los archivos.", content_type="text/plain")

    df = pd.DataFrame(data, columns=['timestamp', 'temperature'])

    # Filtrar datos por hora y fecha si se especifican en los parámetros de la solicitud
    fecha_inicio_str = request.GET.get('fecha_inicio', None)
    fecha_fin_str = request.GET.get('fecha_fin', None)

    if not fecha_inicio_str and not fecha_fin_str:
        # Calcular fecha_inicio y fecha_fin si no están especificadas
        fecha_fin = datetime.now()  # Fecha actual
        fecha_inicio = fecha_fin - timedelta(hours=4)  # 4 horas antes de la fecha actual
    else:
        try:
            fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
            fecha_fin = datetime.fromisoformat(fecha_fin_str)
        except Exception as e:
            return HttpResponse(f"Error al procesar las fechas: {e}", content_type="text/plain")

    df = df[(df['timestamp'] >= fecha_inicio) & (df['timestamp'] <= fecha_fin)]

    

    # Preparar datos para el gráfico
    timestamps = [translate_timestamp(ts) for ts in df['timestamp']]
    temperatures = df['temperature'].tolist()

      # Ordenar los datos de más recientes a más antiguos
    df = df.sort_values(by='timestamp', ascending=False)

    # Preparar datos para la tabla
    table_data = []
    for date, temp in zip(df['timestamp'], df['temperature']):
        date_str = translate_timestamp(date)  # Traducir la fecha y hora a español
        
        # Determinar el color de la temperatura en la tabla según los rangos definidos
        if temp < artefacto1.temp_min or temp > artefacto1.temp_max:
            temp_color = 'red'
        else:
            temp_color = 'blue'
        
        table_data.append({'fecha_hora': date_str, 'temperatura': temp, 'color': temp_color})

    # Renderizar la plantilla con los datos del gráfico
    return render(request, 'mobile/estadisticaM.html', {
        'timestamps': json.dumps(timestamps),
        'temperatures': json.dumps(temperatures),
        'cuenta': artefacto1.cuenta.nombre_cuenta,
        'puerto': artefacto1.puerto,
        'descripcion': artefacto1.artefacto.descripcion,
        'tabla_datos': table_data,
        'datos': artefacto1
    })