
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        "message": "🚗 Welcome to VoltWorth API",
        "description": "Predict Electric Vehicle resale values using machine learning.",
        "endpoints": {
            "Predict price": "/api/predict/",
            "Vehicles list": "/vehicles/",
            "Admin": "/admin/"
        }
    })
