from django.urls import path
from pulso.views import SensorReadingListCreate, SensorReadingDetail
from gestion import views as gestion
from django.contrib import admin
urlpatterns = [
    path('admin/', admin.site.urls), 
    path('sensor_readings/', SensorReadingListCreate.as_view(), name='sensor_reading_list_create'),
    path('sensor_readings/<int:pk>/', SensorReadingDetail.as_view(), name='sensor_reading_detail'),
    path('temperature-graph/<int:cuenta>/<int:puerto>/', gestion.TemperatureGraphView, name='temperature_graph'),


    #cuentas
    path('cuentas/<int:tipo>',gestion.listarCuentas,name='cuentas'),
    path('cuenta/<int:tipo>/<int:id>',gestion.nuevaCuenta,name='nuevaCuenta'),
    path('cuenta/guardar',gestion.guardarCuenta,name='guardarCuenta'),
    path('cuenta/eliminar/<int:tipo>/<int:id>',gestion.eliminarCuenta,name='eliminarCuenta'),


    #artefacto
    path('artefactos/', gestion.listar_artefactos, name='listar_artefactos'),
    path('artefactos/nuevo/<int:id>/', gestion.nuevo_artefacto, name='nuevo_artefacto'),
    path('artefactos/eliminar/<int:id>/', gestion.eliminar_artefacto, name='eliminar_artefacto'),


    #instalaciones
    path('cuenta_has_artefacto/', gestion.listar_cuenta_has_artefacto, name='listar_cuenta_has_artefacto'),
    path('cuenta_has_artefacto/nuevo/<int:id>/', gestion.nueva_cuenta_has_artefacto, name='nueva_cuenta_has_artefacto'),
    path('cuenta_has_artefacto/eliminar/<int:id>/', gestion.eliminar_cuenta_has_artefacto, name='eliminar_cuenta_has_artefacto'),


    #auxiliares
    path('auxiliar/traerPais',gestion.traePais,name='traePais'),
    path('auxiliar/traeProvincias',gestion.traeProvincias,name='traeProvincias'),
    path('auxiliar/traeLocalidad',gestion.traeLocalidad,name='traeLocalidad'),
    path('auxiliar/traeTipoDocumento',gestion.traeTipoDocumento,name='traeTipoDocumento'),
    path('auxiliar/traeTipoIva',gestion.traeTipoIva,name='traeTipoIva'),
]

