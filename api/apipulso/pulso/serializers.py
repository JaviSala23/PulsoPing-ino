from rest_framework import serializers
from .models import SensorReading

class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = '__all__'
        read_only_fields = ('timestamp',)
