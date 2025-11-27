import os
import joblib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Ruta - apuntando a api/models/
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  
MODELS_DIR = os.path.join(BASE_DIR, "api", "models")   

# Rutas a los archivos
MODEL_PATH = os.path.join(MODELS_DIR, "voltworth_price_predictor_cpu.pkl")
METADATA_PATH = os.path.join(MODELS_DIR, "voltworth_metadata.pkl")

# Variables globales
price_predictor = None
feature_info = None
model_loaded_time = None

def load_models():
    """
    Carga los modelos y metadata con verificación de integridad
    """
    global price_predictor, feature_info, model_loaded_time
    
    try:
        if not os.path.exists(MODEL_PATH):
            logger.error(f"Archivo de modelo no encontrado: {MODEL_PATH}")
            return False
            
        if not os.path.exists(METADATA_PATH):
            logger.error(f"Archivo de metadata no encontrado: {METADATA_PATH}")
            return False
        
        # Cargar modelo y metadata
        price_predictor = joblib.load(MODEL_PATH)
        feature_info = joblib.load(METADATA_PATH)
        model_loaded_time = datetime.now()
        
        # Verificar que el modelo tiene los métodos esperados
        if not hasattr(price_predictor, 'predict'):
            logger.error("El modelo cargado no tiene método predict")
            return False
            
        logger.info("✅ Modelos VoltWorth cargados correctamente")
        logger.info(f"📊 Modelo: {feature_info.get('model_info', {}).get('best_model', 'Unknown')}")
        logger.info(f"🎯 MAE: {feature_info.get('performance', {}).get('mae', 'Unknown')} €")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error cargando modelos VoltWorth: {e}")
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
        "model_info": feature_info.get('model_info', {}) if feature_info else {},
        "performance": feature_info.get('performance', {}) if feature_info else {}
    }

# Cargar modelos al importar el módulo
load_models()