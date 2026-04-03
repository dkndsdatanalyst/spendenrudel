import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os
import io

st.set_page_config(page_title="Spendenrudel Map", layout="wide")

# Styling für die Überschrift
st.markdown("<h1 style='text-align: center;'>🐺 #spendenrudel</h1>", unsafe_allow_html=True)

# 1. Pfad-Check
if not os.path.exists('landkreise.json') or not os.path.exists('spender.csv'):
    st.error("⚠️ Dateien fehlen! Stelle sicher, dass landkreise.json und spender.csv im Repository liegen.")
else:
    # 2. Daten laden
    with open('landkreise.json', encoding='utf-8') as f:
        landkreise_geo = json.load(f)
    
    # CSV laden und bereinigen (wichtig gegen den "Berlin-only" Bug)
    with open('spender.csv', 'r', encoding='utf-8') as f:
        content = f.read().replace('\r', '') # Entfernt Windows-Umbrüche
    
    df = pd.read_csv(io.StringIO(content))
    
    # Namen säubern (entfernt unsichtbare Leerzeichen)
    df['landkreis'] = df['landkreis'].astype(str).str.strip()
    df['status'] = pd.to_numeric(df['status'], errors='coerce').fillna(0)

    # 3. Die Karte erstellen
    fig = px.choropleth(
        df,
        geojson=landkreise_geo,
        locations='landkreis',
        featureidkey='properties.krs_name_short',
        color='status',
        color_continuous_scale=[[0, "white"], [1, "#006432"]], # Weiß zu Wolfsburg-Grün
        range_color=[0, 1],
        hover_data={'landkreis': True, 'status': False}
    )

    # 4. Karten-Design & Zoom
    fig.update_geos(
        visible=False,
        fitbounds="geojson", # Zwingt die Ansicht auf alle Landkreise in der JSON
        showcountries=False
    )
    
    fig.update_traces(
        marker_line_width=0.5, 
        marker_line_color="lightgray"
    )
    
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_showscale=False,
        dragmode=False # Karte fest fixieren für Mobile-User
    )

    # 5. Anzeige in Streamlit
    st.plotly_chart(fig, width='stretch')
    
    st.markdown(f"<p style='text-align: center; color: gray;'>Stand: 03.04.2026 | Spenden-Status aktiv</p>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Datenquellen: Landkreise GeoJSON | Visualisierung: #spendenrudel Dashboard")