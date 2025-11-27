from django.contrib import admin
from django.urls import path, include

from django.urls import path
from . import views

urlpatterns = [
    path("predict/", views.predict_vehicle, name="predict_vehicle"),
]
