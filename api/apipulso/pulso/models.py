from django.db import models

class SensorReading(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField()

    def __str__(self):
        return f"{self.timestamp} - {self.temperature}°C"

# Create your models here.
