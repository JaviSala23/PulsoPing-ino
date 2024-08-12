from django.contrib import admin
from .models import Firmware, Placa, SensorReading, MessageLog

@admin.register(Firmware)
class FirmwareAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'version', 'descripcion')
    search_fields = ('nombre', 'version')
    list_filter = ('nombre',)

@admin.register(Placa)
class PlacaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'firmware')
    search_fields = ('codigo', 'descripcion')
    list_filter = ('firmware',)

@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'temperature', 'placa', 'puerto', 'compresor_status', 'puerta_status')
    search_fields = ('placa__codigo', 'puerto')
    list_filter = ('compresor_status', 'puerta_status')
    date_hierarchy = 'timestamp'

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('placa', 'puerto', 'timestamp', 'message_type', 'temperature', 'compresor_status', 'puerta_status')
    search_fields = ('placa__id', 'puerto', 'message_type', 'temperature')
    list_filter = ('message_type', 'compresor_status', 'puerta_status', 'timestamp')

