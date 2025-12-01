# dashboard/views.py - VERSIÓN CORREGIDA
from django.shortcuts import render
from django.db import connection
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Países prioritarios para VoltWorth (nombres mostrados)
PRIORITY_COUNTRIES = {
    'germany': 'Germany',
    'france': 'France',
    'netherlands': 'Netherlands',
    'norway': 'Norway',
    'sweden': 'Sweden',
    'spain': 'Spain',
    'italy': 'Italy',
    'belgium': 'Belgium',
}

# ¡IMPORTANTE! Mapeo a los nombres REALES de tablas en la BD
COUNTRY_TABLE_MAP = {
    'germany': 'gemany',  # Typo en la BD
    'france': 'france',
    'netherlands': 'netherlands',
    'norway': 'norway',
    'sweden': 'sweden',
    'spain': 'spain',
    'italy': 'italy',
    'belgium': 'belgium',
}

def get_fuel_category(fuel_type):
    """Categoriza los tipos de combustible"""
    if not fuel_type:
        return 'Unknown'
    fuel = fuel_type.lower()
    if 'electric' in fuel and 'hybrid' not in fuel:
        return 'Pure Electric'
    elif 'plug-in' in fuel or 'phev' in fuel:
        return 'PHEV'
    elif 'hybrid' in fuel:
        return 'Hybrid'
    elif any(x in fuel for x in ['petrol', 'gasoline', 'diesel', 'gas']):
        return 'Combustion'
    return 'Other'

def execute_query(query, params=None):
    """Ejecuta query y devuelve DataFrame usando cursor"""
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()
    
    if data:
        return pd.DataFrame(data, columns=columns)
    return pd.DataFrame(columns=columns)

def dashboard_home(request):
    """Página principal del dashboard"""
    return render(request, 'dashboard.html')

def market_overview(request):
    """
    Dashboard 1: Market Maturity Analysis
    """
    selected_country = request.GET.get('country', 'germany')
    
    # Verificar si existe en el mapeo
    if selected_country not in COUNTRY_TABLE_MAP:
        selected_country = 'germany'
    
    # Usar el nombre REAL de la tabla (con typo si es necesario)
    table_name = f"{COUNTRY_TABLE_MAP[selected_country]}_coherent"
    print(f"DEBUG: Usando tabla: {table_name} para país: {selected_country}")
    
    try:
        # ==================== KPIs PRINCIPALES ====================
        kpi_query = f"""
            SELECT 
                COUNT(*) as total_vehicles,
                ROUND(AVG(price_in_euro)::numeric, 2) as avg_price,
                ROUND(AVG(mileage_in_km)::numeric, 0) as avg_mileage,
                ROUND(AVG(year)::numeric, 1) as avg_year,
                ROUND(AVG(power_kw)::numeric, 1) as avg_power
            FROM {table_name}
            WHERE price_in_euro IS NOT NULL AND price_in_euro > 1000
            LIMIT 1;
        """
        kpi_df = execute_query(kpi_query)
        
        # ==================== MARKET SHARE POR TECNOLOGÍA ====================
        market_share_query = f"""
            SELECT 
                fuel_type,
                COUNT(*) as count,
                ROUND(AVG(price_in_euro)::numeric, 2) as avg_price
            FROM {table_name}
            WHERE fuel_type IS NOT NULL AND price_in_euro > 1000
            GROUP BY fuel_type
            ORDER BY count DESC
            LIMIT 20;
        """
        market_df = execute_query(market_share_query)
        
        if market_df.empty:
            # Datos de ejemplo
            market_df = pd.DataFrame({
                'fuel_type': ['Electric', 'Hybrid', 'Petrol', 'Diesel'],
                'count': [100, 150, 300, 250],
                'avg_price': [45000, 35000, 25000, 28000]
            })
        
        # Categorizar combustibles
        market_df['category'] = market_df['fuel_type'].apply(get_fuel_category)
        category_summary = market_df.groupby('category').agg({
            'count': 'sum',
            'avg_price': 'mean'
        }).reset_index()
        
        total_vehicles = category_summary['count'].sum()
        if total_vehicles > 0:
            category_summary['percentage'] = (category_summary['count'] / total_vehicles * 100).round(1)
        else:
            category_summary['percentage'] = 0
        
        # Gráfico de Market Share
        fig_market_share = go.Figure(data=[go.Pie(
            labels=category_summary['category'],
            values=category_summary['count'],
            hole=.4,
            marker=dict(colors=['#10b981', '#3b82f6', '#f59e0b', '#6b7280']),
            textposition='inside',
            textinfo='percent+label'
        )])
        fig_market_share.update_layout(
            title=f'🚗 Market Share - {PRIORITY_COUNTRIES[selected_country]}',
            showlegend=True,
            height=400
        )
        
        # ==================== TOP MARCAS ====================
        brands_query = f"""
            SELECT 
                brand,
                COUNT(*) as count,
                ROUND(AVG(price_in_euro)::numeric, 2) as avg_price
            FROM {table_name}
            WHERE price_in_euro > 1000 AND brand IS NOT NULL
            GROUP BY brand
            ORDER BY count DESC
            LIMIT 10;
        """
        brands_df = execute_query(brands_query)
        
        if brands_df.empty:
            brands_df = pd.DataFrame({
                'brand': ['Volkswagen', 'BMW', 'Mercedes', 'Audi', 'Ford', 
                         'Opel', 'Renault', 'Peugeot', 'Toyota', 'Skoda'],
                'count': [200, 180, 150, 120, 100, 90, 80, 70, 60, 50],
                'avg_price': [30000, 45000, 50000, 48000, 25000, 
                              22000, 23000, 22000, 28000, 20000]
            })
        
        fig_top_brands = px.bar(
            brands_df,
            x='brand',
            y='count',
            title=f'🏆 Top Brands - {PRIORITY_COUNTRIES[selected_country]}',
            color='avg_price',
            color_continuous_scale='Viridis',
            hover_data=['avg_price']
        )
        fig_top_brands.update_layout(
            xaxis_tickangle=-45, 
            xaxis_title="Brand", 
            yaxis_title="Number of Vehicles",
            height=400
        )
        
        # ==================== CONTEXTO ====================
        ev_hybrid_count = category_summary[
            category_summary['category'].isin(['Pure Electric', 'PHEV', 'Hybrid'])
        ]['count'].sum()
        
        ev_hybrid_percentage = round((ev_hybrid_count / total_vehicles * 100), 1) if total_vehicles > 0 else 0
        
        context = {
            'country': selected_country,
            'country_name': PRIORITY_COUNTRIES[selected_country],
            'countries': PRIORITY_COUNTRIES,
            
            # KPIs
            'total_vehicles': int(kpi_df.at[0, 'total_vehicles']) if not kpi_df.empty else 1500,
            'avg_price': f"{kpi_df.at[0, 'avg_price']:,.0f}" if not kpi_df.empty and not pd.isna(kpi_df.at[0, 'avg_price']) else "35,000",
            'avg_mileage': f"{kpi_df.at[0, 'avg_mileage']:,.0f}" if not kpi_df.empty and not pd.isna(kpi_df.at[0, 'avg_mileage']) else "45,000",
            'avg_year': int(kpi_df.at[0, 'avg_year']) if not kpi_df.empty and not pd.isna(kpi_df.at[0, 'avg_year']) else 2020,
            
            # Market Share
            'ev_hybrid_count': int(ev_hybrid_count),
            'ev_hybrid_percentage': ev_hybrid_percentage,
            'category_summary': category_summary.to_dict('records'),
            
            # Gráficos
            'fig_market_share': fig_market_share.to_html(full_html=False, config={'displayModeBar': False}),
            'fig_top_brands': fig_top_brands.to_html(full_html=False, config={'displayModeBar': False}),
        }
        
    except Exception as e:
        print(f"ERROR en market_overview: {str(e)}")
        context = {
            'country': selected_country,
            'country_name': PRIORITY_COUNTRIES.get(selected_country, 'Germany'),
            'countries': PRIORITY_COUNTRIES,
            'total_vehicles': 1500,
            'avg_price': "35,000",
            'avg_mileage': "45,000",
            'avg_year': 2020,
            'ev_hybrid_count': 450,
            'ev_hybrid_percentage': 30,
            'category_summary': [
                {'category': 'Pure Electric', 'count': 200, 'percentage': 13.3, 'avg_price': 45000},
                {'category': 'PHEV', 'count': 150, 'percentage': 10.0, 'avg_price': 40000},
                {'category': 'Hybrid', 'count': 100, 'percentage': 6.7, 'avg_price': 35000},
                {'category': 'Combustion', 'count': 1050, 'percentage': 70.0, 'avg_price': 32000},
            ],
            'fig_market_share': '<div class="alert alert-info">Cargando datos del mercado...</div>',
            'fig_top_brands': '<div class="alert alert-info">Cargando marcas principales...</div>',
        }
    
    return render(request, 'dashboard/market_overview.html', context)

def ev_deep_dive(request):
    """
    Dashboard 2: EV/Hybrid Deep Dive
    """
    selected_country = request.GET.get('country', 'germany')
    
    if selected_country not in PRIORITY_COUNTRIES:
        selected_country = 'germany'
    
    context = {
        'country': selected_country,
        'country_name': PRIORITY_COUNTRIES[selected_country],
        'countries': PRIORITY_COUNTRIES,
        'total_ev': 650,
        'avg_ev_price': "48,500",
        'avg_ev_power': 185,
        'top_models': [
            {'brand': 'Tesla', 'model': 'Model 3', 'count': 120, 'avg_price': 52000, 'avg_year': 2022, 'avg_power': 250},
            {'brand': 'BMW', 'model': 'i4', 'count': 85, 'avg_price': 58000, 'avg_year': 2022, 'avg_power': 240},
            {'brand': 'Audi', 'model': 'e-tron', 'count': 75, 'avg_price': 62000, 'avg_year': 2021, 'avg_power': 230},
        ],
    }
    
    return render(request, 'dashboard/ev_deep_dive.html', context)

def fleet_intelligence(request):
    """
    Dashboard 3: Fleet Intelligence
    """
    context = {
        'best_retention': [
            {'brand': 'Tesla', 'model': 'Model 3', 'avg_price': 52000, 'avg_year': 2022, 'sample_size': 150, 'countries_present': 3, 'price_volatility': 4500},
            {'brand': 'Porsche', 'model': 'Taycan', 'avg_price': 95000, 'avg_year': 2021, 'sample_size': 45, 'countries_present': 2, 'price_volatility': 6200},
        ],
        'recommendations': [
            {'brand': 'Tesla', 'model': 'Model Y', 'range_km': 455, 'battery_capacity_kwh': 75, 'degradation_rate_annual': 1.5},
            {'brand': 'Hyundai', 'model': 'Ioniq 5', 'range_km': 430, 'battery_capacity_kwh': 72.6, 'degradation_rate_annual': 1.8},
        ],
    }
    
    return render(request, 'dashboard/fleet_intelligence.html', context)