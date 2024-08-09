from django.contrib import admin
from .models import pais, provincia, localidad, tipo_documento, situacionIva, tipo_cuenta, cuenta, artefacto, Cuenta_has_Artefacto
from pulso.models import Placa  # Si es necesario importar Placa

# Opcional: Clases de administración para personalizar la visualización
class PaisAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ('nombre_provincia', 'codigo_provincia', 'pais_idpais')
    search_fields = ('nombre_provincia', 'codigo_provincia')
    list_filter = ('pais_idpais',)

class LocalidadAdmin(admin.ModelAdmin):
    list_display = ('nombre_localidad', 'cp_localidad', 'provincia_id_provincia')
    search_fields = ('nombre_localidad', 'cp_localidad')
    list_filter = ('provincia_id_provincia',)

class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'cod_afip')
    search_fields = ('descripcion', 'cod_afip')

class SituacionIvaAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'reducida')
    search_fields = ('descripcion', 'reducida')

class TipoCuentaAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)
    search_fields = ('descripcion',)

class CuentaAdmin(admin.ModelAdmin):
    list_display = ('nombre_cuenta', 'numero_documento', 'direccion_cuenta', 'tipo_documento_idtipo_documento', 'pais_id', 'provincia_idprovincia', 'localidad_idlocalidad', 'tipo_cuenta', 'situacionIva_idsituacionIva', 'usuario')
    search_fields = ('nombre_cuenta', 'numero_documento')
    list_filter = ('tipo_documento_idtipo_documento', 'pais_id', 'provincia_idprovincia', 'localidad_idlocalidad', 'tipo_cuenta', 'situacionIva_idsituacionIva', 'usuario')

class ArtefactoAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)
    search_fields = ('descripcion',)

class CuentaHasArtefactoAdmin(admin.ModelAdmin):
    list_display = ('cuenta', 'artefacto', 'placa', 'puerto', 'temp_min', 'temp_max', 'url')
    search_fields = ('cuenta__nombre_cuenta', 'artefacto__descripcion')
    list_filter = ('cuenta', 'artefacto', 'placa')

# Registra los modelos en el panel de administración
admin.site.register(pais, PaisAdmin)
admin.site.register(provincia, ProvinciaAdmin)
admin.site.register(localidad, LocalidadAdmin)
admin.site.register(tipo_documento, TipoDocumentoAdmin)
admin.site.register(situacionIva, SituacionIvaAdmin)
admin.site.register(tipo_cuenta, TipoCuentaAdmin)
admin.site.register(cuenta, CuentaAdmin)
admin.site.register(artefacto, ArtefactoAdmin)
admin.site.register(Cuenta_has_Artefacto, CuentaHasArtefactoAdmin)


# Register your models here.
