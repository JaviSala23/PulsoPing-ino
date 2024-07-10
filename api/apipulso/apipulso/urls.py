from django.urls import path
from pulso.views import SensorReadingListCreate, SensorReadingDetail
from gestion import views as gestion
from django.contrib import admin
urlpatterns = [
    path('admin/', admin.site.urls), 
    path('sensor_readings/', SensorReadingListCreate.as_view(), name='sensor_reading_list_create'),
    path('sensor_readings/<int:pk>/', SensorReadingDetail.as_view(), name='sensor_reading_detail'),
    path('temperature-graph/<int:cuenta>/<int:puerto>/', gestion.TemperatureGraphView, name='temperature_graph'),

    path('admin/', admin.site.urls),

    #cuentas
    path('cuentas/<int:tipo>',gestion.listarCuentas,name='cuentas'),
    path('cuenta/<int:tipo>/<int:id>',gestion.nuevaCuenta,name='nuevaCuenta'),
    path('cuenta/guardar',gestion.guardarCuenta,name='guardarCuenta'),
    path('cuenta/eliminar/<int:tipo>/<int:id>',gestion.eliminarCuenta,name='eliminarCuenta'),

    #auxiliares
    path('auxiliar/traerPais',gestion.traePais,name='traePais'),
    path('auxiliar/traeProvincias',gestion.traeProvincias,name='traeProvincias'),
    path('auxiliar/traeLocalidad',gestion.traeLocalidad,name='traeLocalidad'),
    path('auxiliar/traeTipoDocumento',gestion.traeTipoDocumento,name='traeTipoDocumento'),
    path('auxiliar/traeTipoIva',gestion.traeTipoIva,name='traeTipoIva'),
]

