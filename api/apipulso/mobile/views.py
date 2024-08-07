from django.shortcuts import render
from gestion.models import Cuenta_has_Artefacto
from gestion.views import obtener_ultimo_registro
from django.http import JsonResponse

def panel_view(request):

    relaciones = Cuenta_has_Artefacto.objects.all()

    # Lista para almacenar relaciones junto con sus últimos registros de temperatura
    relaciones_actualizadas = []

    # Itera sobre las relaciones para obtener y agregar el último registro de temperatura
    for relacion in relaciones:
        archivo_path = relacion.url  # Ajusta esto según tu modelo y campo correspondiente
        try:
            ultimo_registro = obtener_ultimo_registro(archivo_path)
        except:
            ultimo_registro=0
        # Agrega un diccionario con la relación y el último registro de temperatura
        relaciones_actualizadas.append({
            'relacion': relacion,
            'ultimo_registro': ultimo_registro
        })

    return render(request, 'mobile/panel.html', {'relaciones_actualizadas': relaciones_actualizadas})

def actualizar_relaciones_mobile(requrest):
    relaciones = Cuenta_has_Artefacto.objects.all()

    # Lista para almacenar relaciones junto con sus últimos registros de temperatura
    relaciones_actualizadas = []

    # Itera sobre las relaciones para obtener y agregar el último registro de temperatura
    for relacion in relaciones:
        archivo_path = relacion.url  # Ajusta esto según tu modelo y campo correspondiente
        ultimo_registro = obtener_ultimo_registro(archivo_path)

        # Convierte la relación a un formato serializable
        relacion_serializable = {
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