from django.contrib import admin
from django.urls import path, include
from voltworth.api import views_v2 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # APIs
    path('api/', include('voltworth.api.urls')),
    
    # Apps
    path('vehicles/', include('voltworth.vehicles.urls')),
    path('dashboard/', include('voltworth.dashboard.urls')),
    
    # Vista demo principal
    path('demo/', views_v2.demo_view, name='demo'),
    path('', views_v2.demo_view, name='home'),
]
