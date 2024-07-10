import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from gestion.models import *
from django.contrib import messages
from django.http import JsonResponse
from gestion.forms import *

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
        formulario.fields['id'].initial=cuenta1.id
        formulario.fields['tipoCuenta'].initial=tipocuenta.id_tipo_cuenta
        formulario.fields['nombre'].initial=cuenta1.nombre
        formulario.fields['TipoDocumento'].choices=[(cuenta1.tipo_documento.idtipo_documento,cuenta1.tipo_documento.descripcion)]
        formulario.fields['numeroDocumento'].initial=cuenta1.numero_documento
        formulario.fields['TipoIva'].choices=[(cuenta1.situacionIva.idsituacionIva,cuenta1.situacionIva.descripcion)]
        formulario.fields['telefono'].initial=cuenta1.telefono
        formulario.fields['celular'].initial=cuenta1.celular
        formulario.fields['email'].initial=cuenta1.email
        formulario.fields['direccion'].initial=cuenta1.direccion
        formulario.fields['paises'].choices=[(cuenta1.pais.id_pais,cuenta1.pais.nombre)]
        formulario.fields['provincia'].choices=[(cuenta1.provincia.id_provincia,cuenta1.provincia.nombre_provincia)]
        formulario.fields['localidad'].choices=[(cuenta1.localidad.id_localidad,cuenta1.localidad.nombre_localidad)]
      
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
            
            cuenta1.nombre = request.POST['nombre']
            cuenta1.numero_documento =request.POST['numeroDocumento']
            cuenta1.direccion= request.POST['direccion']
            cuenta1.telefono = request.POST['telefono']
            cuenta1.email =  request.POST['email']
            cuenta1.celular =  request.POST['celular']
            cuenta1.tipo_documento = tipo_documento.objects.get(pk= request.POST['TipoDocumento'])
            cuenta1.pais = pais.objects.get(pk= request.POST['paises'])
            cuenta1.provincia= provincia.objects.get(pk= request.POST['provincia'])
            cuenta1.localidad = localidad.objects.get(pk=request.POST['localidad'])
            cuenta1.tipo_cuenta=tipocuenta
            cuenta1.situacionIva = situacionIva.objects.get(pk=request.POST['TipoIva'])

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
Monitor temperatura grafico
'''

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
    return render(request, 'monitoreo/graficos.html', {'graph': image_base64})
