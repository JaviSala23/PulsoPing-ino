from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import SensorReading
from .serializers import SensorReadingSerializer

class SensorReadingListCreate(generics.ListCreateAPIView):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer

    def perform_create(self, serializer):
        serializer.save()

class SensorReadingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer

