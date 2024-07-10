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


def panel(request):
    return render(request,'inicio/panelControl.html')




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

    # Lista para almacenar relaciones junto con sus últimos registros de temperatura
    relaciones_actualizadas = []

    # Itera sobre las relaciones para obtener y agregar el último registro de temperatura
    for relacion in relaciones:
        archivo_path = relacion.url  # Ajusta esto según tu modelo y campo correspondiente
        print(archivo_path)
        ultimo_registro = obtener_ultimo_registro(archivo_path)
        print(ultimo_registro)
        # Agrega un diccionario con la relación y el último registro de temperatura
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
                date_str, temp_str, placa, puerto = last_line.split(',')
                ultimo_registro = {
                    'fecha_hora': parse_datetime(date_str),
                    'temperatura': float(temp_str)
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
    if id != 0:
        relacion = get_object_or_404(Cuenta_has_Artefacto, pk=id)
        form = CuentaHasArtefactoForm(instance=relacion)
        funcion = "Modificar"
    else:
        form = CuentaHasArtefactoForm()
        funcion = "Agregar"
    if request.method == 'POST':
        form = CuentaHasArtefactoForm(request.POST, instance=relacion)
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


















'''
Monitor temperatura grafico
'''


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
    dia_semana = DIAS_ESPANOL.get(timestamp.weekday(), '')
    dia_mes = timestamp.day
    mes = MESES_ESPANOL.get(timestamp.month, '')
    ano = timestamp.year
    hora = timestamp.strftime('%H:%M:%S')
    return f"{dia_semana}, {dia_mes} de {mes} de {ano} {hora}"

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
    except Exception as e:
        return HttpResponse(f"Error leyendo archivo {url_clean}: {e}", content_type="text/plain")

    for line in lines:
        parts = line.strip().split(',')
        if len(parts) < 2:
            continue  # Saltar líneas que no cumplen con la estructura esperada

        try:
            timestamp = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
            temperature = float(parts[1])
            dentro_rango = artefacto1.temp_min <= temperature <= artefacto1.temp_max
            data.append((timestamp, temperature, dentro_rango))
        except Exception as e:
            continue

    # Convertir los datos en un DataFrame de pandas
    if not data:
        return HttpResponse("No se encontraron datos válidos en los archivos.", content_type="text/plain")

    df = pd.DataFrame(data, columns=['timestamp', 'temperature', 'dentro_rango'])

    # Aplicar filtro por fecha si se proporcionan parámetros
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    try:
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
    except Exception as e:
        return HttpResponse(f"Error en el filtro de fechas: {e}", content_type="text/plain")

    # Crear un gráfico de puntos con matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Colores basados en el rango de temperatura
    ax.scatter(df['timestamp'], df['temperature'], c=df['dentro_rango'].map({True: 'blue', False: 'red'}))
    
    # Etiquetas completas en los ejes (usando la función translate_timestamp)
    ax.set_xlabel('Fecha y Hora')
    ax.set_ylabel('Temperatura')
    
    # Aplicar formato personalizado de fecha en el eje x
    ax.set_xticks(df['timestamp'])
    ax.set_xticklabels([translate_timestamp(t) for t in df['timestamp']], rotation=45)
    
    # Agregar tooltips con mpld3 para mostrar temperaturas al pasar el mouse por encima
    tooltips = mpld3.plugins.PointLabelTooltip(ax.get_children()[0], labels=list(df['temperature'].astype(str)))
    mpld3.plugins.connect(fig, tooltips)
    
    # Convertir el gráfico en formato HTML interactivo con mpld3
    interactive_graph = mpld3.fig_to_html(fig)
    
    # Guardar el gráfico en un objeto BytesIO para insertarlo en la plantilla
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Codificar la imagen en base64 para poder insertarla en la plantilla
    graph_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # Renderizar la plantilla con el gráfico interactivo y la imagen en base64
    return render(request, 'monitoreo/graficos.html', {'graph': interactive_graph, 'graph_base64': graph_base64})