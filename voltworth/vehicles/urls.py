from django.urls import path
from voltworth.vehicles import views as vehicles_views

urlpatterns = [
    path("predict/", vehicles_views.predict_vehicle, name="predict_vehicle"),
]
