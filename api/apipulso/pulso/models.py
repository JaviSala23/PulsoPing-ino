from django.db import models
from datetime import datetime, timedelta

class Firmware(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(null=False, blank=False, max_length=15)
    version = models.CharField(null=False, blank=False, max_length=15)
    descripcion = models.CharField(null=False, blank=False, max_length=200)

    def __str__(self):
        return f"{self.nombre} - {self.version}"

class Placa(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(null=False, blank=False, max_length=15)
    descripcion = models.CharField(null=False, blank=False, max_length=100)
    firmware = models.ForeignKey(Firmware, null=False, blank=False, on_delete=models.PROTECT)

    def __str__(self):
        return self.codigo

class SensorReading(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField(blank=False, null=False)
    placa = models.ForeignKey(Placa, blank=False, null=False, on_delete=models.PROTECT)
    puerto = models.IntegerField(blank=False, null=False)

    # Nuevos campos para sensores adicionales
    compresor_status = models.BooleanField(default=False)  # True para encendido, False para apagado
    puerta_status = models.BooleanField(default=False)      # True para abierto, False para cerrado

    def __str__(self):
        return f"{self.placa.id}-{self.timestamp} - Temp: {self.temperature}°C, Compresor: {self.compresor_status}, Puerta: {self.puerta_status}"

class MessageLog(models.Model):
    id = models.AutoField(primary_key=True)
    placa = models.ForeignKey(Placa, null=False, blank=False, on_delete=models.PROTECT)
    puerto = models.IntegerField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=50)  # Puede ser "ALERT" o "STABLE"
    temperature = models.FloatField(blank=False, null=False)
    compresor_status = models.BooleanField(default=False)
    puerta_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Placa: {self.placa.id}, Puerto: {self.puerto}, Tipo: {self.message_type}, Temp: {self.temperature}, Timestamp: {self.timestamp}"