from django.urls import path
from pulso.views import SensorReadingListCreate, SensorReadingDetail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sensor_readings/', SensorReadingListCreate.as_view(), name='sensor_reading_list_create'),
    path('sensor_readings/<int:pk>/', SensorReadingDetail.as_view(), name='sensor_reading_detail'),
]