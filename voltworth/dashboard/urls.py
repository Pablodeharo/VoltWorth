from django.urls import path
from . import views

urlpatterns = [
    path('', views.overview, name='dashboard_overview'),
    path('ev/', views.ev_dashboard, name='dashboard_ev'),
]
