# 🚗⚡ VoltWorth - Electric Vehicle Resale Value Predictor

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.0+-green.svg)](https://www.djangoproject.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.0+-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[English](#english)** | **[Español](#español)**

---

<a name="english"></a>
## 🇬🇧 English

### Overview

**VoltWorth** a data science project aimed at predicting the residual value of electric vehicles (EVs) in the European market. Using synthetic data from nine European countries, the system analyzes technical and usage factors—such as range, mileage, and brand—that most influence depreciation, in order to provide accurate resale price estimates.

**Why VoltWorth?**  
Companies in the rental/leasing industry need data-driven insights to optimize their EV fleet purchasing and selling decisions. VoltWorth provides predictive analytics to minimize losses and maximize ROI.

---

### 🎯 Key Features

- **ML Price Prediction**: XGBoost/Random Forest models trained on synthetic and real European EV market data to enhance model robustness and coverage.
- **REST API**: Django-powered endpoints for real-time predictions
- **Feature Engineering**: 9 custom features capturing depreciation patterns (km/year, power-to-battery ratio, age categories)
- **Interactive Dashboard**: Web interface for vehicle price estimation
- **Multi-country Support**: Training data from Denmark, Finland, France, Germany, Italy, Netherlands, Norway, Spain, Sweden

---

### 🏗️ Architecture

```
┌─────────────────┐
│   ML Pipeline   │  ← Training (scikit-learn + XGBoost)
│  (Jupyter/CLI)  │
└────────┬────────┘
         │ Exports model artifacts (.pkl)
         ▼
┌─────────────────────────────────────────┐
│         Django REST API                 │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │ /api/predict │  │ /dashboard/demo │ │
│  │  (JSON)      │  │   (Web UI)      │ │
│  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  voltworth_price│
│  _predictor.pkl │  ← Serialized model + preprocessor
└─────────────────┘
```

**Components**:
- **`/api`**: Model serving via Django REST endpoints
- **`/dashboard`**: Web UI for demos and visualizations
- **`/vehicles`**: Vehicle catalog management
- **`models/`**: Trained ML artifacts (pipeline + metadata)

---

### 🚀 Quick Start

#### 1. Clone Repository

```bash
git clone https://github.com/Pablodeharo/VoltWorth.git
cd voltworth
```

#### 2. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
cd VoltWorth
pip install -r requirements.txt
```

#### 3. Run Django Server

```bash
python manage.py migrate
python manage.py runserver
```

#### 4. Access Demo

- **Demo**: http://localhost:8000/demo/


---

### 📡 API Usage

#### POST `/api/predict/`

**Request**:
```json
{
  "brand": "TESLA",
  "model": "Model 3",
  "country": "Germany",
  "battery_capacity_kWh": 75.0,
  "electric_range_km": 480.0,
  "torque_nm": 450.0,
  "top_speed_kmh": 225.0,
  "seats": 5,
  "drivetrain": "AWD",
  "car_body_type": "Sedan",
  "age_years": 2,
  "km": 20000
}
```

**Response**:
```json
{
  "predicted_price_euro": 42350.75,
  "model_used": "XGBoost",
  "confidence": "high"
}
```

---

### 🧪 Model Details

**Training Pipeline** (see `/pipeline` in ML repo):(https://github.com/Pablodeharo/Voltworth-core/tree/main)
1. **Data Loading**: 15,000+ EV listings from Europe (sintetic)
2. **Feature Engineering**: Creates 9 derived features (usage intensity, efficiency ratios, depreciation categories)
3. **Model Training**: Compares Random Forest, XGBoost, Ridge with GridSearchCV
4. **Evaluation**: Best model selected via MAE (Mean Absolute Error)

**Key Features**:
- `km_per_year`: Usage intensity indicator
- `power_to_battery_ratio`: Efficiency metric
- `age_category`: Non-linear depreciation binning
- `brand_year`: Brand prestige × age interaction

**Performance**:
- **MAE**: ~€2,450 (on test set)
- **R²**: ~0.89

---

### 📂 Project Structure

```
Api-Voltworth-v1.1/
├── voltworth/
│   ├── api/                    # ML model serving
│   │   ├── models/             # Trained artifacts
│   │   ├── model_loader.py     # Model initialization
│   │   └── views_v2.py         # API endpoints
│   ├── dashboard/              # Web UI
│   │   ├── templates/
│   │   └── views.py
│   ├── vehicles/               # Catalog management
│   └── voltworth_config/       # Django settings
├── requirements.txt
├── Procfile                    # Render deployment
└── README.md
```

---

### 🛠️ Tech Stack

**Backend**:
- Django 4.0+ (REST API framework)
- scikit-learn (preprocessing pipelines)
- XGBoost (gradient boosting)
- pandas, numpy (data manipulation)

**Deployment**:
- Render (cloud platform)
- Gunicorn (WSGI server)
- WhiteNoise (static files)

**ML Training** (separate repo):
- Jupyter Notebooks (EDA)
- GridSearchCV (hyperparameter tuning)
- Matplotlib (visualizations)

---

### 🎓 Skills

✅ **End-to-End ML**: From data exploration to production deployment  
✅ **API Development**: RESTful services with Django  
✅ **Feature Engineering**: Domain-driven feature creation for regression tasks  
✅ **Model Deployment**: Serialized models served via web app  
✅ **Software Engineering**: Modular code, separation of concerns, version control

---

### 📊 Use Cases

1. **Fleet Management**: Leasing companies can predict residual values for portfolio optimization
2. **Dynamic Pricing**: Adjust rental rates based on predicted depreciation
3. **Purchase Decisions**: Identify undervalued EVs in the market
4. **Risk Assessment**: Estimate future value for insurance/financing

---

### 🚧 Future Improvements

- [ ] SHAP values(Dashboard)
- [ ] Battery health (SoH) impact on pricing

---

### 👤 Author

[LinkedIn](https://www.linkedin.com/in/pablo-de-haro-pishoudt-0871972b6/)

---

<a name="español"></a>
## 🇪🇸 Español

**VoltWorth** es un proyecto de ciencia de datos orientado a predecir el valor residual de vehículos eléctricos (VE) en el mercado europeo. Basándose en datos de nueve países europeos (sintéticos), la plataforma analiza los factores técnicos y de uso que más afectan la depreciación—como la autonomía, el kilometraje y la marca—para proporcionar estimaciones precisas de los precios de reventa.  
Empresas de renting/leasing (como Revel) necesitan análisis basados en datos para optimizar decisiones de compra y venta de flotas eléctricas. VoltWorth proporciona analítica predictiva para minimizar pérdidas y maximizar ROI.

---

### 🎯 Características Principales

- **Predicción ML de Precios**: Predicción ML de Precios: Modelos XGBoost/Random Forest entrenados con datos europeos (reales y sintéticos) de vehículos eléctricos.
- **API REST**: Endpoints Django para predicciones en tiempo real
- **Feature Engineering**: 9 features personalizadas que capturan patrones de depreciación
- **Dashboard Interactivo**: Interfaz web para estimación de precios
- **Soporte Multi-país**: Datos de Dinamarca, Finlandia, Francia, Alemania, Italia, Países Bajos, Noruega, España, Suecia

---

### 🚀 Inicio Rápido

#### 1. Clonar Repositorio

```bash
git clone https://github.com/Pablodeharo/VoltWorth.git
cd VoltWorth
cd voltworth
```

#### 2. Instalar Dependencias

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Ejecutar Servidor Django

```bash
python manage.py migrate
python manage.py runserver
```

#### 4. Acceder a Demo

- **Demo**: http://localhost:8000/demo/

---

### 📡 Uso de la API

#### POST `/api/predict/`

**Petición**:
```json
{
  "brand": "TESLA",
  "model": "Model 3",
  "country": "Germany",
  "battery_capacity_kWh": 75.0,
  "electric_range_km": 480.0,
  "torque_nm": 450.0,
  "top_speed_kmh": 225.0,
  "seats": 5,
  "drivetrain": "AWD",
  "car_body_type": "Sedan",
  "age_years": 2,
  "km": 20000
}
```

**Respuesta**:
```json
{
  "predicted_price_euro": 42350.75,
  "model_used": "XGBoost",
  "confidence": "high"
}
```

---

### 🧪 Detalles del Modelo

**Pipeline de Entrenamiento**ML-Repo(https://github.com/Pablodeharo/Voltworth-core/tree/main)
1. **Carga de Datos**: 15,000+ anuncios de VE de mercados europeos
2. **Feature Engineering**: Crea 9 features derivadas (intensidad de uso, ratios de eficiencia, categorías de depreciación)
3. **Entrenamiento**: Compara Random Forest, XGBoost, Ridge con GridSearchCV
4. **Evaluación**: Mejor modelo seleccionado mediante MAE

**Features Clave**:
- `km_per_year`: Indicador de intensidad de uso
- `power_to_battery_ratio`: Métrica de eficiencia
- `age_category`: Categorización no lineal de depreciación
- `brand_year`: Interacción prestigio de marca × edad

**Rendimiento**:
- **MAE**: ~€2,450 (en test set)
- **R²**: ~0.89

---

### 🛠️ Stack Tecnológico

**Backend**:
- Django 4.0+ (framework REST API)
- scikit-learn (pipelines de preprocesamiento)
- XGBoost (gradient boosting)
- pandas, numpy (manipulación de datos)

**Despliegue**:
- Render (plataforma cloud)
- Gunicorn (servidor WSGI)
- WhiteNoise (archivos estáticos)

---

### 🎓 Habilidades

✅ **ML End-to-End**: Desde exploración de datos hasta despliegue en producción  
✅ **Desarrollo de APIs**: Servicios RESTful con Django  
✅ **Feature Engineering**: Creación de features orientadas al dominio  
✅ **Despliegue de Modelos**: Modelos serializados servidos vía aplicación web  
✅ **Ingeniería de Software**: Código modular, separación de responsabilidades

---

### 📊 Casos de Uso

1. **Gestión de Flotas**: Empresas de leasing predicen valores residuales para optimizar portfolio
2. **Pricing Dinámico**: Ajustar tarifas de alquiler según depreciación predicha
3. **Decisiones de Compra**: Identificar VE infravalorados en el mercado
4. **Evaluación de Riesgo**: Estimar valor futuro para seguros/financiación

---

### 🚧 Mejoras Futuras

- [ ] Valores SHAP
- [ ] Impacto de salud de batería (SoH) en pricing


---

### 👤 Autor

**Pablo**
[LinkedIn](https://www.linkedin.com/in/pablo-de-haro-pishoudt-0871972b6/)

---
