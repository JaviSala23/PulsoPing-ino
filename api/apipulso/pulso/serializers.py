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

    class Meta:
        model = SensorReading
        fields = ['temperature', 'placa', 'puerto', 'timestamp', 'compresor_status', 'puerta_status', 'energia_status']
        read_only_fields = ('timestamp',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        print(f"Lectura temperatura: {representation['temperature']}, Placa: {representation['placa']}, Puerto: {representation['puerto']}, Puerta: {representation.get('puerta_status')}, Compresor: {representation.get('compresor_status')}, Energia: {representation.get('energia_status')}")
        return representation

    def create(self, validated_data):
        sensor_reading = SensorReading.objects.create(**validated_data)
        return sensor_reading