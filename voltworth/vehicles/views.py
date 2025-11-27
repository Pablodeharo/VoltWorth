# views.py
from django.shortcuts import render
import pandas as pd
import joblib
import os
import numpy as np
from django.conf import settings
from django.http import JsonResponse

# ==== CARGA SEGURA DEL MODELO ====
MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'voltworth_price_predictor.pkl')
METADATA_PATH = os.path.join(settings.BASE_DIR, 'models', 'voltworth_metadata.pkl')

try:
    model = joblib.load(MODEL_PATH)
    metadata = joblib.load(METADATA_PATH)
    print("✅ Modelo VoltWorth y metadata cargados correctamente.")
except Exception as e:
    print(f"❌ Error al cargar el modelo: {e}")
    model, metadata = None, None

def predict_vehicle(request):
    """
    Vista principal para predecir precio de vehículos eléctricos
    """
    prediction = None
    error = None
    input_data = {}
    
    if request.method == "POST":
        try:
            # Recoger datos del formulario
            input_data = {
                'brand': request.POST.get("brand", "").strip(),
                'model': request.POST.get("model", "").strip(),
                'car_body_type': request.POST.get("car_body_type", "").strip(),
                'country': request.POST.get("country", "").strip(),
                'mileage_in_km': float(request.POST.get("mileage_in_km", 0)),
                'power_kw': float(request.POST.get("power_kw", 0)),
                'range_km': float(request.POST.get("range_km", 0)),
                'battery_capacity_kWh': float(request.POST.get("battery_capacity_kWh", 0)),
                
                # Features opcionales - usar valores por defecto si no se proporcionan
                'acceleration_0_100_s': float(request.POST.get("acceleration_0_100_s", 
                                        metadata['default_values']['acceleration_0_100_s'])),
                'top_speed_kmh': float(request.POST.get("top_speed_kmh", 
                                      metadata['default_values']['top_speed_kmh'])),
                'age': float(request.POST.get("age", metadata['default_values']['age'])),
                'seats': int(request.POST.get("seats", metadata['default_values']['seats'])),
                'drivetrain': request.POST.get("drivetrain", 
                                metadata['default_values']['drivetrain']).strip()
            }
            
            # Validar datos requeridos
            required_fields = ['brand', 'model', 'country', 'car_body_type']
            for field in required_fields:
                if not input_data[field]:
                    error = f"El campo {field} es obligatorio"
                    break
            
            if not error and model:
                # Crear DataFrame con todas las features en el orden correcto
                prediction_df = pd.DataFrame([input_data])
                
                # Asegurar que todas las columnas están presentes
                for feature in metadata['all_features']:
                    if feature not in prediction_df.columns:
                        prediction_df[feature] = metadata['default_values'].get(feature, 0)
                
                # Reordenar columnas como el modelo espera
                prediction_df = prediction_df[metadata['all_features']]
                
                # Hacer predicción
                raw_prediction = model.predict(prediction_df)[0]
                prediction = max(0, round(raw_prediction, 2))  # Evitar precios negativos
                
        except ValueError as e:
            error = f"Error en los datos numéricos: {e}"
        except Exception as e:
            error = f"Error al procesar la predicción: {e}"

    # Contexto para el template
    context = {
        'prediction': prediction,
        'error': error,
        'input_data': input_data,
        'valid_categories': metadata.get('valid_categories', {}) if metadata else {},
        'default_values': metadata.get('default_values', {}) if metadata else {}
    }
    
    return render(request, "vehicles/predict.html", context)

def predict_vehicle_api(request):
    """
    API endpoint para aplicaciones externas
    """
    if request.method == "POST":
        try:
            data = request.POST.dict()
            
            # Preparar datos de entrada
            input_data = {}
            for feature in metadata['all_features']:
                if feature in data:
                    # Convertir a tipo adecuado
                    if feature in ['brand', 'model', 'country', 'drivetrain', 'car_body_type']:
                        input_data[feature] = str(data[feature])
                    else:
                        input_data[feature] = float(data[feature])
                else:
                    # Usar valor por defecto
                    input_data[feature] = metadata['default_values'].get(feature, 0)
            
            # Crear DataFrame y predecir
            prediction_df = pd.DataFrame([input_data])[metadata['all_features']]
            raw_prediction = model.predict(prediction_df)[0]
            prediction = max(0, round(raw_prediction, 2))
            
            return JsonResponse({
                'success': True,
                'prediction': prediction,
                'currency': 'EUR'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
