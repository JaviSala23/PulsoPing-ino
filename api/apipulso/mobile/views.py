from django.shortcuts import render,redirect
from gestion.models import Cuenta_has_Artefacto
from pulso.models import Placa
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
from django.contrib import messages
from django.contrib.auth import logout


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

def login_view(request):
    # Obtener el nombre de usuario
    username = request.user.username
    if username:
        return redirect('panelMobile') 
    else:
        error_message = request.GET.get('error', None)
        form = AuthenticationForm()
        context = {
            'form': form,
            'error_message': error_message
        }
        return render(request, 'mobile/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('login_mobile') 

def authenticate_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()  # Obtiene el usuario autenticado
            auth_login(request, user)  # Autentica al usuario y establece la sesión
            return redirect('panelMobile')  # Redirige a una vista protegida

        else:  
            messages.error(request, f'Usuario y contraseña invalidos')
            return redirect('login_mobile')  # Redirige al formulario de inicio de sesión en caso de error
    else:
        messages.error(request,f'Usuario y contraseña invalidos')
        return redirect('login_mobile') 

def panel_view(request):
    # Obtener el nombre de usuario
    username = request.user.username
    if username:

        # Filtrar las relaciones según el grupo del usuario
        if request.user.groups.filter(name='Clientes').exists():
            relaciones = Cuenta_has_Artefacto.objects.filter(cuenta__usuario=request.user)  # Ajusta este filtro según tu modelo
        
            print(relaciones)
        if request.user.groups.filter(name='Administrador').exists():
            relaciones = Cuenta_has_Artefacto.objects.all()  # No mostrar nada si no es del grupo "Clientes"
        
        

        
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
    else:
        messages.error(request,f'Usuario y contraseña invalidos')
        return redirect('login_mobile') 

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
        artefacto1 = Cuenta_has_Artefacto.objects.get(pk=id)
    except Cuenta_has_Artefacto.DoesNotExist:
        return HttpResponse("No se encontró el artefacto especificado.", content_type="text/plain")
    
    data = []
    
    try:
        url_clean = artefacto1.url.strip()

        with open(url_clean, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        return HttpResponse(f"Error leyendo archivo {url_clean}: {e}", content_type="text/plain")

    for line in lines:
        parts = line.strip().split(',')
        if len(parts) < 6:  # Asegúrate de que haya al menos 6 partes en la línea
            continue

        try:
            timestamp = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
            temperature = float(parts[1])
            if artefacto1.placa.firmware.puerta:
                puerta = 1 if parts[5].strip().lower() == 'true' else 0
            else:
                puerta=None
            if artefacto1.placa.firmware.compresor:
                compresor = 1 if parts[4].strip().lower() == 'true' else 0
            else:
                compresor=None
            data.append((timestamp, temperature, puerta, compresor))
        except Exception as e:
            continue

    if not data:
        return HttpResponse("No se encontraron datos válidos en los archivos.", content_type="text/plain")

    df = pd.DataFrame(data, columns=['timestamp', 'temperature', 'puerta', 'compresor'])

    # Filtrar por fecha y hora
    fecha_inicio_str = request.GET.get('fecha_inicio', None)
    fecha_fin_str = request.GET.get('fecha_fin', None)

    if not fecha_inicio_str and not fecha_fin_str:
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(hours=4)
    else:
        try:
            fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
            fecha_fin = datetime.fromisoformat(fecha_fin_str)
        except Exception as e:
            return HttpResponse(f"Error al procesar las fechas: {e}", content_type="text/plain")

    df = df[(df['timestamp'] >= fecha_inicio) & (df['timestamp'] <= fecha_fin)]

    

    timestamps = [translate_timestamp(ts) for ts in df['timestamp']]
    temperatures = df['temperature'].tolist()
    puerta_states = df['puerta'].tolist()
    compresor_states = df['compresor'].tolist()
    df = df.sort_values(by='timestamp', ascending=False)
    table_data = []
    for date, temp, puerta, compresor in zip(df['timestamp'], df['temperature'], df['puerta'], df['compresor']):
        date_str = translate_timestamp(date)
        
        # Determina el color basado en los límites de temperatura
        temp_color = 'red' if temp < artefacto1.temp_min or temp > artefacto1.temp_max else 'blue'
        
        table_data.append({
            'fecha_hora': date_str, 
            'temperatura': temp, 
            'color': temp_color, 
            'puerta': 'Abierta' if puerta == 1 else 'Cerrada' if puerta == 0 else None, 
            'compresor': 'Encendido' if compresor == 1 else 'Apagado' if compresor == 0 else None
        })

    return render(request, 'mobile/estadisticaM.html', {
        'timestamps': json.dumps(timestamps),
        'temperatures': json.dumps(temperatures),
        'puerta_states': json.dumps(puerta_states),
        'compresor_states': json.dumps(compresor_states),
        'cuenta': artefacto1.cuenta.nombre_cuenta,
        'descripcion': artefacto1.artefacto.descripcion,
        'tabla_datos': table_data,
        'datos': artefacto1
    })


@api_view(['POST'])
def check_device_view(request):
    # Obtener los datos JSON del cuerpo de la solicitud
    placa = request.data.get('codigo')
    puerto = request.data.get('puerto')

    
    # Validar que ambos parámetros estén presentes
    if not placa or not puerto:
        return Response({'error': 'Faltan parámetros'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        placa1=Placa.objects.get(codigo=placa)
        # Verificar si existe una entrada con el placa y puerto dados
        device_exists = Cuenta_has_Artefacto.objects.filter(placa=placa1, puerto=puerto).exists()

        # Devolver la respuesta en JSON
        if device_exists:
            return Response({'valid': True}, status=status.HTTP_200_OK)
        else:
            return Response({'valid': False}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_device_status(request):
    # Obtener los datos de los parámetros de la URL
    placa_codigo = request.query_params.get('placa')
    puerto_codigo = request.query_params.get('puerto')

    # Validar que ambos parámetros estén presentes
    if not placa_codigo or not puerto_codigo:
        return Response({'error': 'Faltan parámetros'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Buscar el objeto Placa y manejar si no existe
        placa = get_object_or_404(Placa, codigo=placa_codigo)

        # Filtrar por placa y puerto
        dispositivos = Cuenta_has_Artefacto.objects.filter(placa=placa, puerto=puerto_codigo)

        # Crear una lista para almacenar los datos de respuesta
        relaciones_actualizadas = []

        # Iterar sobre los dispositivos y obtener el último registro de cada uno
        for dispositivo in dispositivos:
            archivo_path = dispositivo.url  # Ajusta esto según tu modelo y campo correspondiente
            ultimo_registro = obtener_ultimo_registro(archivo_path)

            # Verificar si se obtuvo un último registro
            if ultimo_registro:
                data = {
                    'temperature': ultimo_registro['temperatura'],
                    'energyStatus': None,  # Añade lógica si necesitas este campo
                    'doorStatus': ultimo_registro['puerta'],
                    'compressorStatus': ultimo_registro['compresor'],
                    'dateTime': ultimo_registro['fecha_hora'],
                }
                relaciones_actualizadas.append(data)
            else:
                return Response({'error': 'No se pudo obtener el último registro del archivo'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Devolver la lista de dispositivos con sus últimos registros
        return Response({'relaciones_actualizadas': relaciones_actualizadas}, status=status.HTTP_200_OK)

    except Placa.DoesNotExist:
        return Response({'error': 'Placa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
