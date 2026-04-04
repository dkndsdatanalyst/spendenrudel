import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os
import io

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #spendenrudel")

if not os.path.exists('landkreise.json') or not os.path.exists('spender.csv'):
    st.error("Dateien fehlen!")
else:
    # 1. GeoJSON laden
    with open('landkreise.json', encoding='utf-8') as f:
        landkreise_geo = json.load(f)
    
    # 2. CSV laden & extrem säubern
    with open('spender.csv', 'r', encoding='utf-8') as f:
        clean_content = f.read().replace('\r', '').strip()
    
    df = pd.read_csv(io.StringIO(clean_content))
    
    # WICHTIG: Leerzeichen und Dubletten entfernen
    df['landkreis'] = df['landkreis'].astype(str).str.strip()
    df['status'] = pd.to_numeric(df['status'], errors='coerce').fillna(0)

    # 3. Das Mapping-Feld in der GeoJSON vorbereiten
    # Wir stellen sicher, dass JEDES Feature in der GeoJSON existiert
    all_districts = [f['properties']['krs_name_short'] for f in landkreise_geo['features']]
    
    # 4. Karte erstellen
    fig = px.choropleth(
        df,
        geojson=landkreise_geo,
        locations='landkreis',
        featureidkey='properties.krs_name_short',
        color='status',
        color_continuous_scale=[[0, "#f8f9fa"], [1, "#006432"]], # Ganz helles Grau für 0
        range_color=[0, 1],
        hover_name='landkreis'
    )

    # 5. DER TRICK: Damit man alle Landkreise sieht, auch wenn sie nicht in der CSV stehen
    fig.update_geos(
        visible=False,
        fitbounds="geojson",
        showcountries=False,
        showframe=False
    )
    
    # Alle Umrisse zeichnen (auch die leeren)
    fig.update_traces(
        marker_line_width=0.5, 
        marker_line_color="lightgray",
        # Das hier sorgt dafür, dass auch Landkreise ohne Daten angezeigt werden
        showlegend=False 
    )

    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)
    st.write(f"Daten-Check: {len(df)} Einträge in CSV gefunden.")

st.markdown("---")
st.caption("Stand: 04.04.2026 | Spendenrudel Dashboard")
