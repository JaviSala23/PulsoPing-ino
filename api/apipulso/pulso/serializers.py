from rest_framework import serializers
from .models import SensorReading, Placa

class PlacaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Placa
        fields = ['id', 'codigo']  # Ajusta los campos según tus necesidades

class SensorReadingSerializer(serializers.ModelSerializer):
    placa = serializers.PrimaryKeyRelatedField(queryset=Placa.objects.all())
    compresor_status = serializers.BooleanField(required=False, allow_null=True)
    puerta_status = serializers.BooleanField(required=False, allow_null=True)
    energia_status = serializers.BooleanField(required=False, allow_null=True)
    humidity = serializers.FloatField(required=False, allow_null=True)  # Nuevo campo

    class Meta:
        model = SensorReading
        fields = ['temperature', 'humidity', 'placa', 'puerto', 'timestamp', 'compresor_status', 'puerta_status', 'energia_status']
        read_only_fields = ('timestamp',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        print(f"Lectura -> Temp: {representation['temperature']}°C, Humedad: {representation.get('humidity', 'N/A')}%, Placa: {representation['placa']}, Puerto: {representation['puerto']}")
        return representation

    def create(self, validated_data):
        return SensorReading.objects.create(**validated_data)
