# api/views_v2.py
from django.http import JsonResponse
from django.shortcuts import render
import json
from .model_loader import price_predictor, feature_info, load_models
from django.db import connection
import pandas as pd
import traceback


# cargar modelos
if price_predictor is None:
    load_models()


def predict_value(request):
    try:
        print("\n" + "="*60)
        print("🔵 NUEVA PETICIÓN DE PREDICCIÓN")
        print("="*60)
        
        # Parse request
        data = json.loads(request.body)
        print(f"📥 Datos recibidos: {json.dumps(data, indent=2)}")
        
        # Crear DataFrame
        df = pd.DataFrame([data])
        print(f"📊 Columnas iniciales del DataFrame: {df.columns.tolist()}")

        # Engineered features
        print("\n🔧 Creando features ingenierizadas...")
        df["vehicle_age"] = df["age_years"]
        df["km_per_year"] = df["km"] / df["age_years"].replace(0, 1)
        df["age_category"] = pd.cut(df["age_years"], bins=[0,3,7,20], labels=["new","mid","old"])
        df["mileage_category"] = pd.cut(df["km"], bins=[0,30000,60000,200000], labels=["low","med","high"])
        df["brand_year"] = df["brand"] + "_" + df["age_years"].astype(str)
        df["power_to_battery_ratio"] = df["torque_nm"] / df["battery_capacity_kWh"]
        df["power_age_interaction"] = df["torque_nm"] / df["age_years"].replace(0, 1)
        df["km_per_torque"] = df["km"] / df["torque_nm"].replace(0, 1)
        df["km_per_speed"] = df["km"] / df["top_speed_kmh"].replace(0, 1)
        
        print(f"✅ Features después de ingeniería: {df.columns.tolist()}")

        # Expected features
        expected_features = (
            feature_info["features"]["numeric"] +
            feature_info["features"]["categorical"]
        )
        print(f"\n📋 Features esperadas por el modelo: {expected_features}")

        # Verificar qué columnas faltan
        missing_cols = set(expected_features) - set(df.columns)
        if missing_cols:
            print(f"⚠️  COLUMNAS FALTANTES: {missing_cols}")
            return JsonResponse({
                "error": f"Faltan columnas: {', '.join(missing_cols)}",
                "expected": expected_features,
                "received": df.columns.tolist()
            }, status=400)

        # Seleccionar solo las features esperadas
        df = df[expected_features]
        print(f"✅ DataFrame final para predicción: {df.shape}")
        print(f"   Columnas: {df.columns.tolist()}")
        
        # Predicción
        print("\n🤖 Realizando predicción...")
        base_pred = price_predictor.predict(df)[0]
        print(f"💰 Predicción base: €{base_pred:,.2f}")

        # Ajustes de mercado
        adjustments = {
            "Finland": 1.12,
            "Germany": 1.08,
            "Spain": 0.93,
            "France": 1.02,
            "Belgium": 1.01,
            "Italy": 0.97
        }

        result = {}
        for country, factor in adjustments.items():
            result[country] = round(float(base_pred) * factor, 2)  # -> convierte a float

        print(f"\n✅ RESULTADO FINAL:")
        for country, price in result.items():
            print(f"   {country}: €{price:,.2f}")
        print("="*60 + "\n")

        return JsonResponse(result)

    except KeyError as e:
        error_msg = f"Columna faltante: {str(e)}"
        print(f"\n❌ ERROR KeyError: {error_msg}")
        traceback.print_exc()
        return JsonResponse({
            "error": error_msg,
            "type": "KeyError",
            "available_columns": df.columns.tolist() if 'df' in locals() else []
        }, status=400)
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ ERROR: {error_msg}")
        traceback.print_exc()
        return JsonResponse({
            "error": error_msg,
            "type": type(e).__name__
        }, status=400)




def model_info(request):
    info = {
        "loaded": price_predictor is not None,
        "model_info": feature_info.get('model_info', {}),
        "performance": feature_info.get('performance', {})
    }
    return JsonResponse(info)


def demo_view(request):
    return render(request, "demo.html")


def market_data(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT country, price_in_euro, battery_capacity_kWh, electric_range_km
            FROM vehicles
        """)
        rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns=["country","price_in_euro","battery_capacity_kWh","electric_range_km"])

    data = {
        "country": df["country"].tolist(),
        "price_avg": df.groupby("country")["price_in_euro"].mean().tolist(),
        "battery_capacity": df["battery_capacity_kWh"].tolist(),
        "electric_range_km": df["electric_range_km"].tolist()
    }

    return JsonResponse(data)


def dashboard(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT country, price_in_euro FROM vehicles")
        rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns=["country", "price"])

    avg_price = (
        df.groupby("country")["price"]
        .mean()
        .sort_values(ascending=False)
        .to_dict()
    )

    data_bar = [{
        "x": list(avg_price.keys()),
        "y": list(avg_price.values()),
        "type": "bar"
    }]

    return render(request, "dashboard.html", {
        "avg_price_per_country": data_bar
    })
