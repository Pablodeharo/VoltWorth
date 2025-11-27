from django.urls import path
from . import views_v2

urlpatterns = [
    # Endpoint de predicción
    path('predict/', views_v2.predict_value, name='api_predict'),
    
    # Info del modelo
    path('model-info/', views_v2.model_info, name='api_model_info'),
    
    # Datos de mercado
    path('market-data/', views_v2.market_data, name='api_market_data'),
    
    # Dashboard (si lo quieres en /api/dashboard/)
    path('dashboard/', views_v2.dashboard, name='api_dashboard'),
]