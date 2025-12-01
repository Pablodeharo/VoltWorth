from django.urls import path
from . import views

#app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('market/', views.market_overview, name='market_overview'),
    path('ev/', views.ev_deep_dive, name='ev_deep_dive'),
    path('fleet/', views.fleet_intelligence, name='fleet_intelligence'),
]