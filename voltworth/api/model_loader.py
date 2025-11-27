# api/model_loader.py - VERSIÓN CORREGIDA
import os
import logging
import joblib
from datetime import datetime

logger = logging.getLogger(__name__)

# Rutas CORRECTAS - solo archivos nuevos
CURRENT_DIR = os.path.dirname(__file__)
MODELS_DIR = os.path.join(CURRENT_DIR, "models")

# ⚠️ SOLO estos dos archivos - ELIMINAR voltworth_feature_info.pkl
MODEL_PATH = os.path.join(MODELS_DIR, "voltworth_price_predictor_cpu.pkl")
METADATA_PATH = os.path.join(MODELS_DIR, "voltworth_metadata.pkl")

# Variables globales
price_predictor = None
feature_info = None
model_loaded_time = None

def load_models():
    """
    Carga los modelos y metadata
    """
    global price_predictor, feature_info, model_loaded_time
    
    logger.info(f"🔍 Cargando modelos desde: {MODELS_DIR}")
    
    try:
        # Verificar que los archivos NUEVOS existen
        if not os.path.exists(MODEL_PATH):
            logger.error(f"❌ Modelo no encontrado: {MODEL_PATH}")
            return False
            
        if not os.path.exists(METADATA_PATH):
            logger.error(f"❌ Metadata no encontrada: {METADATA_PATH}")
            return False
        
        # Cargar SOLO los archivos nuevos
        logger.info("📦 Cargando predictor de precios...")
        price_predictor = joblib.load(MODEL_PATH)
        
        logger.info("📦 Cargando metadata del modelo...")
        feature_info = joblib.load(METADATA_PATH)  # ⚠️ Esto REEMPLAZA el viejo feature_info
        
        model_loaded_time = datetime.now()
        
        # Verificaciones del modelo
        if not hasattr(price_predictor, 'predict'):
            logger.error("❌ El modelo cargado no tiene método predict")
            return False
            
        logger.info("✅ Modelo VoltWorth y metadata cargados correctamente")
        logger.info(f"📊 Modelo: {feature_info.get('model_info', {}).get('best_model', 'Unknown')}")
        logger.info(f"🎯 Rendimiento: MAE = {feature_info.get('performance', {}).get('mae', 'Unknown')} €")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error cargando los modelos: {e}")
        price_predictor = None
        feature_info = None
        return False

def get_model_status():
    """
    Retorna el estado actual del modelo
    """
    return {
        "loaded": price_predictor is not None,
        "load_time": model_loaded_time.isoformat() if model_loaded_time else None,
        "model_path": MODEL_PATH,
        "metadata_path": METADATA_PATH,
        "model_info": feature_info.get('model_info', {}) if feature_info else {},
        "performance": feature_info.get('performance', {}) if feature_info else {}
    }

# Cargar modelos al importar el módulo
load_models()