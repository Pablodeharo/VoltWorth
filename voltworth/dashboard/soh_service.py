# dashboard/services/soh_service.py
import os
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from django.db import connection
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings("ignore")

# --------------------------
# RUTAS & CONSTANTES
# --------------------------
# project root (voltworth/)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = PROJECT_ROOT / "models"
SOH_MODEL_PATH = MODELS_DIR / "soh_model.pkl"
SOH_INFO_PATH = MODELS_DIR / "soh_feature_info.pkl"

# Asegurar carpeta models existe
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------
# UTIL: lectura SQL a DataFrame
# --------------------------
def load_ev_degradation_table(limit=None):
    """
    Lee la tabla ev_database_with_degradation desde la BD usando django.db.connection.
    Devuelve un DataFrame pandas.
    """
    sql = "SELECT * FROM ev_database_with_degradation"
    if limit:
        sql += f" LIMIT {int(limit)}"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        cols = [c[0] for c in cursor.description]
        rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=cols)
    return df

# --------------------------
# SOH: Cálculo teórico (engineering baseline)
# --------------------------
def compute_soh_theoretical(row):
    """
    Calcula SOH teórico (en %), usando columnas:
      - battery_capacity_kWh
      - battery_capacity_remaining_1y_kWh  (si existe)
      - battery_deg_1y_pct (si existe)
      - degradation_rate_annual (si existe)
    Fallbacks: intenta varias columnas.
    """
    try:
        bat_kwh = row.get("battery_capacity_kWh")
        if pd.notna(row.get("battery_capacity_remaining_1y_kWh")) and pd.notna(bat_kwh) and bat_kwh > 0:
            soh = (row.get("battery_capacity_remaining_1y_kWh") / bat_kwh) * 100.0
            return float(np.clip(soh, 0, 100))
        # fallback: usar battery_deg_1y_pct
        if pd.notna(row.get("battery_deg_1y_pct")):
            soh = 100.0 - float(row.get("battery_deg_1y_pct"))
            return float(np.clip(soh, 0, 100))
        # fallback: usar degradation_rate_annual
        if pd.notna(row.get("degradation_rate_annual")):
            soh = 100.0 - (float(row.get("degradation_rate_annual")) * 100.0)
            return float(np.clip(soh, 0, 100))
    except Exception:
        pass
    return None

# --------------------------
# Entrenamiento ML: SOH adjuster
# --------------------------
DEFAULT_FEATURES = [
    "battery_capacity_kWh",
    "degradation_rate_annual",
    "charge_ratio",
    "drive_factor",
    "eff_penalty",
    "fast_charging_power_kw_dc",
]

def train_soh_model(df, features=DEFAULT_FEATURES, target_col="soh_target"):
    """
    Entrena un RandomForest para ajustar SOH.
    Guarda modelo y metadata en MODELS_DIR.
    """
    df_train = df.copy()
    # keep only rows with all features & target
    X = df_train[features].replace([np.inf, -np.inf], np.nan)
    y = df_train[target_col]
    valid_mask = X.notnull().all(axis=1) & y.notnull()
    X_valid = X[valid_mask]
    y_valid = y[valid_mask]

    if X_valid.shape[0] < 10:
        print("soh_service: no hay suficientes filas para entrenar un modelo ML (necesario >=10).")
        return None, None

    X_train, X_test, y_train, y_test = train_test_split(
        X_valid, y_valid, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=150, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # evaluar
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"soh_service: modelo SOH entrenado. MAE = {mae:.3f} (porcentaje de SOH)")

    # guardar
    try:
        joblib.dump(model, SOH_MODEL_PATH)
        joblib.dump({"features": features, "target_col": target_col}, SOH_INFO_PATH)
        print(f"soh_service: modelo guardado en {SOH_MODEL_PATH}")
    except Exception as e:
        print("soh_service: fallo guardando modelo:", e)

    return model, {"mae": mae, "n_train": len(X_train)}

def load_soh_model():
    """
    Carga el modelo SOH si existe.
    """
    if SOH_MODEL_PATH.exists() and SOH_INFO_PATH.exists():
        try:
            model = joblib.load(SOH_MODEL_PATH)
            info = joblib.load(SOH_INFO_PATH)
            return model, info
        except Exception as e:
            print("soh_service: fallo cargando modelo existente:", e)
    return None, None

# --------------------------
# Función para preparar dataset y target
# --------------------------
def prepare_soh_dataset(df):
    """
    Prepara dataset con features y target (soh_target) usando columnas disponibles.
    Target: soh_target = computed from battery_capacity_remaining_1y_kWh / battery_capacity_kWh *100
    """
    df2 = df.copy()

    # compute soh_target where possible
    def _compute_target(r):
        try:
            if pd.notna(r.get("battery_capacity_remaining_1y_kWh")) and pd.notna(r.get("battery_capacity_kWh")) and r.get("battery_capacity_kWh") > 0:
                return (r.get("battery_capacity_remaining_1y_kWh") / r.get("battery_capacity_kWh")) * 100.0
            # fallback: use battery_deg_1y_pct if present
            if pd.notna(r.get("battery_deg_1y_pct")):
                return 100.0 - float(r.get("battery_deg_1y_pct"))
        except Exception:
            pass
        return np.nan

    df2["soh_target"] = df2.apply(_compute_target, axis=1)
    # compute soh_theoretical baseline
    df2["soh_theoretical"] = df2.apply(lambda r: compute_soh_theoretical(r), axis=1)

    return df2

# --------------------------
# API principal: get_vehicle_soh & get_fleet_soh
# --------------------------
def _ensure_model_trained(df):
    """
    Carga modelo si existe; si no existe o insuficiente, lo entrena.
    """
    model, info = load_soh_model()
    if model is not None:
        return model, info

    print("soh_service: No se encontró modelo SOH pre-entrenado. Intentando entrenar...")
    df_prepared = prepare_soh_dataset(df)
    model, info = train_soh_model(df_prepared)
    return model, info

def get_vehicle_soh(brand=None, model_name=None):
    """
    Devuelve SOH combinado para un par brand/model (si model_name es None devuelve por brand).
    """
    df = load_ev_degradation_table()
    # Filtrar por brand/model si se dan
    if brand:
        df = df[df["brand"].str.lower() == str(brand).lower()]
    if model_name:
        df = df[df["model"].str.lower() == str(model_name).lower()]

    if df.empty:
        return {"error": "No data for requested brand/model", "count": 0}

    df_prepared = prepare_soh_dataset(df)

    # Baseline: soh_teorico = median of soh_theoretical
    soh_theo_median = float(df_prepared["soh_theoretical"].median()) if df_prepared["soh_theoretical"].notnull().any() else None

    # Load or train model
    model, info = _ensure_model_trained(df_prepared)

    soh_ml_preds = None
    if model is not None:
        features = joblib.load(SOH_INFO_PATH)["features"]
        X = df_prepared[features].fillna(0)
        try:
            soh_ml_preds = model.predict(X)
            soh_ml_median = float(np.median(soh_ml_preds))
        except Exception as e:
            print("soh_service: error prediciendo con modelo ML:", e)
            soh_ml_median = None
    else:
        soh_ml_median = None

    # Combine: weighted average (ej.: 0.6 * teorico + 0.4 * ml) si ambos existen
    if soh_theo_median is not None and soh_ml_median is not None:
        soh_final = round(0.6 * soh_theo_median + 0.4 * soh_ml_median, 2)
    elif soh_theo_median is not None:
        soh_final = round(soh_theo_median, 2)
    elif soh_ml_median is not None:
        soh_final = round(soh_ml_median, 2)
    else:
        soh_final = None

    # aggregate degradation stats
    stats = {
        "count": int(len(df_prepared)),
        "soh_theoretical_median": soh_theo_median,
        "soh_ml_median": soh_ml_median if model is not None else None,
        "soh_final": soh_final,
        "degradation_year1_pct_median": float(df_prepared["battery_deg_1y_pct"].median()) if "battery_deg_1y_pct" in df_prepared.columns and df_prepared["battery_deg_1y_pct"].notnull().any() else None,
        "degradation_year2_pct_median": float(df_prepared["battery_deg_2y_pct"].median()) if "battery_deg_2y_pct" in df_prepared.columns and df_prepared["battery_deg_2y_pct"].notnull().any() else None,
        "degradation_year3_pct_median": float(df_prepared["battery_deg_3y_pct"].median()) if "battery_deg_3y_pct" in df_prepared.columns and df_prepared["battery_deg_3y_pct"].notnull().any() else None,
    }

    return stats

def get_fleet_soh(limit_per_brand=50):
    """
    Devuelve un resumen por brand+model con SOH final y métricas para visualizar en el dashboard.
    limit_per_brand: limita la cantidad de filas leídas por brand para acelerar el cálculo en datasets grandes.
    """
    df = load_ev_degradation_table()
    if df.empty:
        return {"error": "No data in ev_database_with_degradation"}

    # Opcionalmente limitar filas por brand (simple)
    # Para acelerar agrupaciones grandes, tomamos head(limit_per_brand) por brand
    sampled = df.groupby(["brand", "model"]).head(limit_per_brand).reset_index(drop=True)

    prepared = prepare_soh_dataset(sampled)

    # Entrenar / cargar modelo global usando la muestra
    model, info = _ensure_model_trained(prepared)

    features = None
    soh_ml_preds = None
    if model is not None and SOH_INFO_PATH.exists():
        info_loaded = joblib.load(SOH_INFO_PATH)
        features = info_loaded["features"]
        X = prepared[features].fillna(0)
        try:
            soh_ml_preds = model.predict(X)
            prepared["soh_ml_pred"] = soh_ml_preds
        except Exception as e:
            print("soh_service: fallo predicción en get_fleet_soh:", e)

    # Build summary per brand/model
    rows = []
    grouped = prepared.groupby(["brand", "model"])
    for (brand, model_name), g in grouped:
        soh_theo = float(g["soh_theoretical"].median()) if g["soh_theoretical"].notnull().any() else None
        soh_ml_med = float(np.median(g["soh_ml_pred"])) if "soh_ml_pred" in g.columns and g["soh_ml_pred"].size > 0 else None
        if soh_theo is not None and soh_ml_med is not None:
            soh_final = round(0.6 * soh_theo + 0.4 * soh_ml_med, 2)
        elif soh_theo is not None:
            soh_final = round(soh_theo, 2)
        elif soh_ml_med is not None:
            soh_final = round(soh_ml_med, 2)
        else:
            soh_final = None

        rows.append({
            "brand": brand,
            "model": model_name,
            "count": int(len(g)),
            "soh_theoretical_median": soh_theo,
            "soh_ml_median": soh_ml_med,
            "soh_final": soh_final,
            "degradation_year1_pct_median": float(g["battery_deg_1y_pct"].median()) if "battery_deg_1y_pct" in g.columns and g["battery_deg_1y_pct"].notnull().any() else None,
            "degradation_year3_pct_median": float(g["battery_deg_3y_pct"].median()) if "battery_deg_3y_pct" in g.columns and g["battery_deg_3y_pct"].notnull().any() else None,
            "avg_fast_charging_kw": float(g["fast_charging_power_kw_dc"].median()) if "fast_charging_power_kw_dc" in g.columns and g["fast_charging_power_kw_dc"].notnull().any() else None,
            "avg_charge_ratio": float(g["charge_ratio"].median()) if "charge_ratio" in g.columns and g["charge_ratio"].notnull().any() else None,
        })

    # sort by soh_final desc
    rows_sorted = sorted(rows, key=lambda r: (r["soh_final"] is not None, r["soh_final"]), reverse=True)
    # return top 200
    return {"summary": rows_sorted[:200], "model_info": info}
