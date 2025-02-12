import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import mpld3
from datetime import datetime
from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from gestion.models import *
from django.contrib import messages
from django.http import JsonResponse
from gestion.forms import *

from django.utils.dateparse import parse_datetime
import os
from django.template.loader import render_to_string
from matplotlib.dates import DateFormatter
from mpld3 import fig_to_html, plugins
import json
from datetime import datetime, timedelta
from django.contrib.auth.views import LoginView as DjangoLoginView

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy


from io import BytesIO
import base64
import qrcode



class LoginView(DjangoLoginView):
    template_name = 'login_desktop.html'
    redirect_authenticated_user = True



def panel(request):
    return render(request,'panel/panelControl.html')




#auxiliares

def traePais(request):
    if request.method == 'GET':
        paises=pais.objects.all().order_by('nombre')
        return JsonResponse(list(paises.values('id_pais', 'nombre')), safe = False) 

def traeProvincias(request):
    if request.method == 'GET':
        id = request.GET['pais_id']
        provincias=provincia.objects.filter(pais_idpais_id=id).order_by('nombre_provincia')
        return JsonResponse(list(provincias.values('id_provincia', 'nombre_provincia')), safe = False) 

def traeLocalidad(request):
    if request.method == 'GET':
        id = request.GET['provincia_id']
        localidades=localidad.objects.filter(provincia_id_provincia_id=id).order_by('nombre_localidad')
        return JsonResponse(list(localidades.values('id_localidad', 'nombre_localidad')), safe = False)     
def traeTipoDocumento(request):
    if request.method == 'GET':
        tDocumento=tipo_documento.objects.all().order_by('descripcion')
        return JsonResponse(list(tDocumento.values('idtipo_documento', 'descripcion')), safe = False) 
def traeTipoIva(request):
    if request.method == 'GET':
        tIvao=situacionIva.objects.all().order_by('descripcion')
        return JsonResponse(list(tIvao.values('idsituacionIva', 'descripcion')), safe = False) 
    

def listarCuentas(request,tipo):
    tipocuenta=tipo_cuenta.objects.get(pk=tipo)
    cuentas=cuenta.objects.filter(tipo_cuenta=tipocuenta)
    print(tipocuenta)
    return render(request,'cuentas/cuenta.html',{"tipoCuenta":tipocuenta, "cuentas":cuentas})


def nuevaCuenta(request,tipo,id):
    tipocuenta=tipo_cuenta.objects.get(pk=tipo)
    formulario=FormCuenta()
    funcion=""
    if id!=0:
        funcion="Modificar"
        cuenta1=cuenta.objects.get(pk=id)
        formulario.fields['id'].initial=cuenta1.id_cuenta
        formulario.fields['tipoCuenta'].initial=tipocuenta.id_tipo_cuenta
        formulario.fields['nombre'].initial=cuenta1.nombre_cuenta
        formulario.fields['TipoDocumento'].choices=[(cuenta1.tipo_documento_idtipo_documento.idtipo_documento,cuenta1.tipo_documento.descripcion)]
        formulario.fields['numeroDocumento'].initial=cuenta1.numero_documento
        formulario.fields['TipoIva'].choices=[(cuenta1.situacionIva_idsituacionIva.idsituacionIva,cuenta1.situacionIva.descripcion)]
        formulario.fields['telefono'].initial=cuenta1.telefono_cuenta
        formulario.fields['celular'].initial=cuenta1.celular_cuenta
        formulario.fields['email'].initial=cuenta1.email_cuenta
        formulario.fields['direccion'].initial=cuenta1.direccion_cuenta
        formulario.fields['paises'].choices=[(cuenta1.pais_id.id_pais,cuenta1.pais.nombre)]
        formulario.fields['provincia'].choices=[(cuenta1.provincia_idprovincia.id_provincia,cuenta1.provincia.nombre_provincia)]
        formulario.fields['localidad'].choices=[(cuenta1.localidad_idlocalidad.id_localidad,cuenta1.localidad.nombre_localidad)]
      
    else:    
        funcion="Agregar"
        formulario.fields['id'].initial=0
        formulario.fields['tipoCuenta'].initial=tipocuenta.id_tipo_cuenta

    return render(
            request, 
            "cuentas/nuevaCuenta.html",
            {'form':formulario, 'tipoCuenta':tipocuenta, 'funcion':funcion})


def guardarCuenta(request):
    if request.method=='POST':
        tipocuenta = tipo_cuenta.objects.get(pk=request.POST['tipoCuenta'])
     
        try:
            id=request.POST['id']
            
            if id!="0":
                cuenta1=cuenta.objects.get(pk=id)
            else:
                cuenta1=cuenta()
            
            cuenta1.nombre_cuenta = request.POST['nombre']
            cuenta1.numero_documento =request.POST['numeroDocumento']
            cuenta1.direccion_cuenta= request.POST['direccion']
            cuenta1.telefono_cuenta = request.POST['telefono']
            cuenta1.email_cuenta =  request.POST['email']
            cuenta1.celular_cuenta =  request.POST['celular']
            cuenta1.tipo_documento_idtipo_documento = tipo_documento.objects.get(pk= request.POST['TipoDocumento'])
            cuenta1.pais_id = pais.objects.get(pk= request.POST['paises'])
            cuenta1.provincia_idprovincia= provincia.objects.get(pk= request.POST['provincia'])
            cuenta1.localidad_idlocalidad = localidad.objects.get(pk=request.POST['localidad'])
            cuenta1.tipo_cuenta=tipocuenta
            cuenta1.situacionIva_idsituacionIva = situacionIva.objects.get(pk=request.POST['TipoIva'])

            cuenta1.save()
            messages.success(request, f'Se ha guardado el : {tipocuenta.descripcion}')
            return redirect('cuentas', tipo=tipocuenta.id_tipo_cuenta)
        
        except:

            messages.error(request, f'No se pudo guardar el : {tipocuenta.descripcion}')
            return redirect('cuentas', tipo=tipocuenta.id_tipo_cuenta)
        
        
def eliminarCuenta(request,tipo,id):
    tipocuenta = tipo_cuenta.objects.get(pk=tipo)
    cuenta1=cuenta.objects.get(pk=id)
    cuenta1.delete()
    messages.success(request, f'Se ha eliminado la cuenta : {cuenta1.nombre}')
    return redirect('cuentas', tipo=tipocuenta.id_tipo_cuenta)

'''
Crear artefactos
'''

def listar_artefactos(request):
    artefactos = artefacto.objects.all()
    return render(request, 'artefactos/listar_artefactos.html', {'artefactos': artefactos})

def nuevo_artefacto(request, id=0):
    if id != 0:
        artefacto1 = get_object_or_404(artefacto, pk=id)
        form = ArtefactoForm(instance=artefacto1)
        funcion = "Modificar"
    else:
        artefacto1 = None
        form = ArtefactoForm()
        funcion = "Agregar"
    if request.method == 'POST':
        form = ArtefactoForm(request.POST, instance=artefacto1)
        if form.is_valid():
            form.save()
            messages.success(request, f'Se ha {funcion.lower()}do el artefacto correctamente')
            return redirect('listar_artefactos')
        else:
            messages.error(request, 'No se pudo guardar el artefacto')
    return render(request, 'artefactos/nuevo_artefacto.html', {'form': form, 'funcion': funcion})

def eliminar_artefacto(request, id):
    artefacto1 = get_object_or_404(artefacto, pk=id)
    artefacto1.delete()
    messages.success(request, f'Se ha eliminado el artefacto: {artefacto1.descripcion}')
    return redirect('listar_artefactos')


'''
Cuenta Has Artefacto
'''


def listar_cuenta_has_artefacto(request):
    relaciones = Cuenta_has_Artefacto.objects.all()

    # Lista para almacenar relaciones junto con sus últimos registros de temperatura y humedad
    relaciones_actualizadas = []

    # Itera sobre las relaciones para obtener y agregar el último registro de temperatura y humedad
    for relacion in relaciones:
        archivo_path = relacion.url  # Ajusta esto según tu modelo y campo correspondiente
        try:
            ultimo_registro = obtener_ultimo_registro(archivo_path)
        except:
            ultimo_registro = None

        # Agrega un diccionario con la relación y el último registro de datos
        relaciones_actualizadas.append({
            'relacion': relacion,
            'ultimo_registro': ultimo_registro
        })

    return render(request, 'artefactos/listar_cuenta_has_artefacto.html', {'relaciones_actualizadas': relaciones_actualizadas})

def obtener_ultimo_registro(archivo_path):
    ultimo_registro = None
    url_clean = archivo_path.strip()

    if url_clean and os.path.isfile(url_clean):
        with open(url_clean, 'r') as file:
            lines = file.readlines()
            if lines:
                last_line = lines[-1].strip()
                parts = last_line.split(',')

                # Asignar valores con comprobación de longitud
                date_str = parts[0]  # Fecha
                temp_str = parts[1]  # Temperatura
                humedad_str = parts[2] if len(parts) > 2 else "N/A"  # Humedad opcional
                placa = parts[3]  # Placa
                puerto = parts[4]  # Puerto
                compresor = parts[5]  # Compresor
                energia = parts[6] if len(parts) > 6 else 'true'  # Energia con valor por defecto
                puerta = parts[7] if len(parts) > 7 else 'true'  # Puerta con valor por defecto

                # Convertir las cadenas a booleanos y flotantes
                compresor = compresor.strip().lower() == 'true'
                puerta = puerta.strip().lower() == 'true'
                energia = energia.strip().lower() == 'true'
                humedad = float(humedad_str) if humedad_str != "N/A" else None

                ultimo_registro = {
                    'fecha_hora': parse_datetime(date_str),
                    'temperatura': float(temp_str),
                    'humedad': humedad,
                    'compresor': compresor,
                    'puerta': puerta,
                    'energia': energia
                }

    return ultimo_registro

def actualizar_relaciones(request):
    relaciones = Cuenta_has_Artefacto.objects.all()

    # Lista para almacenar relaciones junto con sus últimos registros de temperatura
    relaciones_actualizadas = []

    # Itera sobre las relaciones para obtener y agregar el último registro de temperatura
    for relacion in relaciones:
        archivo_path = relacion.url  # Ajusta esto según tu modelo y campo correspondiente
        ultimo_registro = obtener_ultimo_registro(archivo_path)

        # Agrega un diccionario con la relación y el último registro de temperatura
        relaciones_actualizadas.append({
            'relacion': relacion,
            'ultimo_registro': ultimo_registro
        })

    # Renderizar solo el contenido de la tabla
    tabla_html = render_to_string('artefactos/tabla_relaciones.html', {'relaciones_actualizadas': relaciones_actualizadas})
    
    return JsonResponse({'tabla_html': tabla_html})


def nueva_cuenta_has_artefacto(request, id=0):
    relacion = None
    if id != 0:
        relacion = get_object_or_404(Cuenta_has_Artefacto, pk=id)
        form = CuentaHasArtefactoForm(instance=relacion)
        funcion = "Modificar"
    else:
        form = CuentaHasArtefactoForm()
        funcion = "Agregar"
        
    if request.method == 'POST':
        if relacion is not None:
            form = CuentaHasArtefactoForm(request.POST, instance=relacion)
        else:
            form = CuentaHasArtefactoForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Se ha {funcion.lower()}do la relación correctamente')
            return redirect('listar_cuenta_has_artefacto')
        else:
            messages.error(request, 'No se pudo guardar la relación')
            
    return render(request, 'artefactos/nueva_cuenta_has_artefacto.html', {'form': form, 'funcion': funcion})

def eliminar_cuenta_has_artefacto(request, id):
    relacion = get_object_or_404(Cuenta_has_Artefacto, pk=id)
    relacion.delete()
    messages.success(request, f'Se ha eliminado la relación')
    return redirect('listar_cuenta_has_artefacto')



















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

def TemperatureGraphView(request, cuenta, puerto):
    try:
        artefacto1 = Cuenta_has_Artefacto.objects.get(cuenta=cuenta, puerto=puerto)
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
                puerta = None
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

    return render(request, 'monitoreo/graficos.html', {
        'timestamps': json.dumps(timestamps),
        'temperatures': json.dumps(temperatures),
        'puerta_states': json.dumps(puerta_states),
        'compresor_states': json.dumps(compresor_states),
        'cuenta': artefacto1.cuenta.nombre_cuenta,
        'puerto': puerto,
        'descripcion': artefacto1.artefacto.descripcion,
        'tabla_datos': table_data,
        'datos': artefacto1
    })


def creadorCodigoBarra(request):
     # Obtener los datos de la solicitud GET
    nombre = request.GET.get('nombre')
    codigo = request.GET.get('codigo')
    puerto = request.GET.get('puerto')
    print(nombre,codigo,puerto)

    # Formatear los datos
    data = f"{nombre},{codigo},{puerto}"

    # Crear un objeto QRCode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Crear una imagen del QRCode
    img = qr.make_image(fill='black', back_color='white')

    # Crear un objeto BytesIO para almacenar la imagen
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')

    # Obtener el contenido de la imagen en formato base64
    img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

    # Construir el contexto para la plantilla HTML
    context = {
        'img_data': img_data,
        'data': data,
    }

    # Renderizar la plantilla HTML
    return render(request, 'artefactos/codigoBarra.html', context)