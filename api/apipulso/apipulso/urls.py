from django.urls import path,include
from django.contrib.auth.views import *
from pulso.views import SensorReadingListCreate, SensorReadingDetail
from gestion import views as gestion
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from mobile import views as mobile 
urlpatterns = [

    path('',gestion.panel,name='panel'),
    path('panel/',gestion.panel,name='panel'),
    path('adSite/',admin.site.urls),
  

    #url Autenticacion de usuarios
    path('login/', LoginView.as_view(), name= 'login'),
    path('logout/', LogoutView.as_view(), name= 'logout'),
    path('accounts/', include('django.contrib.auth.urls')),
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
    path('actualizar_relaciones/', gestion.actualizar_relaciones, name='actualizar_relaciones'),
    path('cuenta_has_artefacto/nuevo/<int:id>/', gestion.nueva_cuenta_has_artefacto, name='nueva_cuenta_has_artefacto'),
    path('cuenta_has_artefacto/eliminar/<int:id>/', gestion.eliminar_cuenta_has_artefacto, name='eliminar_cuenta_has_artefacto'),


    #auxiliares
    path('auxiliar/traerPais',gestion.traePais,name='traePais'),
    path('auxiliar/traeProvincias',gestion.traeProvincias,name='traeProvincias'),
    path('auxiliar/traeLocalidad',gestion.traeLocalidad,name='traeLocalidad'),
    path('auxiliar/traeTipoDocumento',gestion.traeTipoDocumento,name='traeTipoDocumento'),
    path('auxiliar/traeTipoIva',gestion.traeTipoIva,name='traeTipoIva'),


    #mobile

    path('mobile/panel',mobile.panel_view,name='panelMobile'),
    path('mobile/actualizar_relaciones',mobile.actualizar_relaciones_mobile,name='actualizar_relaciones_mobile'),
    path('temperature-graphM/<int:id>', mobile.TemperatureGraphView, name='temperature_graphM'),
    path('mobile/login', mobile_login_view, name='login_mobile'),
   
]

