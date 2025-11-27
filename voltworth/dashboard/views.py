# dashboard/views.py
from django.shortcuts import render
from django.db import connection
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

def overview(request):
    """Dashboard principal unificado para análisis de mercado EV"""
    country = request.GET.get('country', 'Spain')
    
    # Validar país
    ALLOWED_COUNTRIES = {'spain','germany','france','italy','portugal','belgium',
                        'netherlands','poland','sweden','norway','denmark','austria'}
    if country.lower() not in ALLOWED_COUNTRIES:
        country = 'Spain'
    
    table_name = f"{country.lower()}_coherent"
    
    # ==================== KPI PRINCIPALES ====================
    kpi_query = f"""
        SELECT 
            COUNT(*) as total_vehicles,
            ROUND(AVG(price_in_euro)::numeric, 2) as avg_price,
            ROUND(AVG(power_kw)::numeric, 1) as avg_power,
            ROUND(AVG(year)::numeric, 1) as avg_year
        FROM {table_name}
        WHERE price_in_euro IS NOT NULL;
    """
    kpi_df = pd.read_sql_query(kpi_query, connection)
    
    # ==================== ANÁLISIS EV ESPECÍFICO ====================
    ev_query = f"""
        SELECT 
            COUNT(*) as ev_count,
            ROUND(AVG(price_in_euro)::numeric, 2) as ev_avg_price,
            ROUND(AVG(power_kw)::numeric, 1) as ev_avg_power
        FROM {table_name}
        WHERE fuel_type ILIKE '%electric%' AND price_in_euro IS NOT NULL;
    """
    ev_df = pd.read_sql_query(ev_query, connection)
    
    # ==================== GRÁFICOS PRINCIPALES ====================
    
    # 1. Distribución de precios por tipo de combustible
    fuel_query = f"""
        SELECT 
            COALESCE(fuel_type, 'Unknown') as fuel_type,
            COUNT(*) as count,
            ROUND(AVG(price_in_euro)::numeric, 2) as avg_price
        FROM {table_name}
        WHERE price_in_euro IS NOT NULL
        GROUP BY fuel_type
        ORDER BY avg_price DESC
        LIMIT 8;
    """
    fuel_df = pd.read_sql_query(fuel_query, connection)
    
    fig_fuel = px.bar(
        fuel_df, 
        x='fuel_type', 
        y='avg_price',
        title='💰 Precio Medio por Tipo de Combustible',
        color='avg_price',
        color_continuous_scale='Viridis'
    )
    fig_fuel.update_layout(xaxis_tickangle=-45)
    
    # 2. Evolución temporal de precios (usando year si registration_date no existe)
    trend_query = f"""
        SELECT 
            ROUND(year) as reg_year,
            ROUND(AVG(price_in_euro)::numeric, 2) as avg_price,
            COUNT(*) as vehicle_count
        FROM {table_name}
        WHERE year IS NOT NULL AND price_in_euro IS NOT NULL
        GROUP BY ROUND(year)
        HAVING COUNT(*) > 5
        ORDER BY reg_year;
    """
    trend_df = pd.read_sql_query(trend_query, connection)
    
    fig_trend = px.line(
        trend_df, 
        x='reg_year', 
        y='avg_price',
        title='📈 Evolución de Precios por Año',
        markers=True
    )
    fig_trend.update_traces(line=dict(width=3))
    
    # 3. Mapa de calor: Potencia vs Precio
    heatmap_query = f"""
        SELECT 
            ROUND(power_kw/50)*50 as power_bin,
            ROUND(year/2)*2 as year_bin,
            ROUND(AVG(price_in_euro)::numeric, 2) as avg_price,
            COUNT(*) as count
        FROM {table_name}
        WHERE power_kw IS NOT NULL AND year IS NOT NULL AND price_in_euro IS NOT NULL
        GROUP BY power_bin, year_bin
        HAVING COUNT(*) > 5;
    """
    heatmap_df = pd.read_sql_query(heatmap_query, connection)
    
    fig_heatmap = px.density_heatmap(
        heatmap_df,
        x='year_bin',
        y='power_bin',
        z='avg_price',
        title='🔥 Relación: Año vs Potencia vs Precio',
        color_continuous_scale='Blues'
    )
    
    # ==================== MÉTRICAS COMPARATIVAS EV vs COMBUSTIÓN ====================
    comparison_query = f"""
        SELECT 
            CASE 
                WHEN fuel_type ILIKE '%electric%' THEN 'Eléctrico'
                WHEN fuel_type ILIKE '%hybrid%' THEN 'Híbrido'
                ELSE 'Combustión'
            END as vehicle_type,
            COUNT(*) as count,
            ROUND(AVG(price_in_euro)::numeric, 2) as avg_price,
            ROUND(AVG(power_kw)::numeric, 1) as avg_power,
            ROUND(AVG(year)::numeric, 1) as avg_year
        FROM {table_name}
        WHERE price_in_euro IS NOT NULL
        GROUP BY vehicle_type;
    """
    comparison_df = pd.read_sql_query(comparison_query, connection)
    
    context = {
        'country': country,
        'total_vehicles': kpi_df.at[0, 'total_vehicles'] if not kpi_df.empty else 0,
        'avg_price': f"{kpi_df.at[0, 'avg_price']:,.0f}" if not kpi_df.empty and kpi_df.at[0, 'avg_price'] is not None else "0",
        'avg_power': kpi_df.at[0, 'avg_power'] if not kpi_df.empty and kpi_df.at[0, 'avg_power'] is not None else 0,
        'avg_year': kpi_df.at[0, 'avg_year'] if not kpi_df.empty and kpi_df.at[0, 'avg_year'] is not None else 0,
        
        'ev_count': ev_df.at[0, 'ev_count'] if not ev_df.empty and ev_df.at[0, 'ev_count'] is not None else 0,
        'ev_avg_price': f"{ev_df.at[0, 'ev_avg_price']:,.0f}" if not ev_df.empty and ev_df.at[0, 'ev_avg_price'] is not None else "0",
        
        'fig_fuel': fig_fuel.to_html(full_html=False),
        'fig_trend': fig_trend.to_html(full_html=False),
        'fig_heatmap': fig_heatmap.to_html(full_html=False),
        
        'comparison_data': comparison_df.to_dict('records'),
        'allowed_countries': sorted(ALLOWED_COUNTRIES),
    }
    
    return render(request, 'dashboard/overview.html', context)

from django.shortcuts import render
from .soh_service import get_fleet_soh

def ev_dashboard(request):
    """
    Dashboard especializado en vehículos eléctricos (SOH + KPIs).
    Esta versión delega en dashboard.services.soh_service.get_fleet_soh()
    para obtener el resumen por marca/model y presenta KPIs/plots.
    """
    try:
        soh_result = get_fleet_soh(limit_per_brand=80)  # ajustar si dataset grande
        summary = soh_result.get("summary", [])
        model_info = soh_result.get("model_info", {})
        # KPIs agregados
        soh_values = [r["soh_final"] for r in summary if r["soh_final"] is not None]
        avg_soh = round(float(pd.Series(soh_values).median()), 2) if len(soh_values) > 0 else None

        # construir contexto para template
        context = {
            "soh_avg": avg_soh,
            "soh_summary": summary,
            "soh_model_info": model_info,
        }
    except Exception as e:
        print("Error en ev_dashboard (soh):", e)
        context = {
            "soh_avg": None,
            "soh_summary": [],
            "soh_model_info": {},
            "error": str(e),
        }

    return render(request, "dashboard/ev_dashboard.html", context)
