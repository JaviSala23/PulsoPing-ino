from rest_framework import serializers
from .models import SensorReading

class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = '__all__'
        read_only_fields = ('timestamp',)

    def to_representation(self, instance):
        # Llama al método de la superclase para obtener la representación
        representation = super().to_representation(instance)
        
        # Verifica si 'timestamp' está en la representación y, si es así, imprímelo en la terminal
        if 'timestamp' in representation:
            print(f"Accessed timestamp: {representation['timestamp']}")
        
        return representation