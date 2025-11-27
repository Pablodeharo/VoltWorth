from django.contrib import admin
from django.urls import path, include
from api import views_v2

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # APIs
    path('api/', include('api.urls')),
    
    # Apps
    path('vehicles/', include('vehicles.urls')),
    path('dashboard/', include('dashboard.urls')),
    
    # Vista demo principal
    path('demo/', views_v2.demo_view, name='demo'),
    path('', views_v2.demo_view, name='home'),
]