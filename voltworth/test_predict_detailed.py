# test_predict_detailed.py
import requests
import json
import sys
import os

# Agregar el path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_prediction_detailed():
    print("🎯 PRUEBA DETALLADA DE PREDICCIÓN")
    print("=" * 50)
    
    url = "http://localhost:8000/api/predict/"
    
    # Datos de prueba
    test_data = {
        "brand": "Tesla",
        "model": "Model 3",
        "year": 2020,
        "mileage_km": 50000,
        "range_km": 400,
        "battery_capacity_kwh": 75,
        "power_kw": 150,
        "country": "Germany"
    }
    
    print("📤 Enviando datos:")
    print(json.dumps(test_data, indent=2))
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=30
        )
        
        print(f"\n📥 Respuesta recibida:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ¡PREDICCIÓN EXITOSA!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("❌ ERROR EN LA PREDICCIÓN")
            print(f"   Respuesta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_prediction_detailed()