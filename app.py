import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os
import io

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #spendenrudel")

# Check ob Dateien da sind
if not os.path.exists('landkreise.json') or not os.path.exists('spender.csv'):
    st.error("Dateien fehlen! Bitte landkreise.json und spender.csv im Ordner anlegen.")
else:
    # 1. Daten laden
    with open('landkreise.json', encoding='utf-8') as f:
        landkreise_geo = json.load(f)
    
    with open('spender.csv', 'r', encoding='utf-8') as f:
        clean_content = f.read().replace('\r', '').strip()
    
    df = pd.read_csv(io.StringIO(clean_content))
    df['landkreis'] = df['landkreis'].str.strip()
    df['status'] = pd.to_numeric(df['status'], errors='coerce').fillna(0)

    # DEBUG AUSGABEN (Nur zum Prüfen, danach kannst du sie löschen)
    st.write("JSON-Beispiel Namen:", [f['properties'].get('krs_name_short', 'KEY FEHLT!') for f in landkreise_geo['features'][:5]])
    st.write("CSV Namen:", df['landkreis'].tolist())

    st.write(f"Anzahl der Landkreise in der JSON: {len(landkreise_geo['features'])}")
    st.write("Die ersten 10 Namen in der JSON:", [f['properties'].get('krs_name_short') for f in landkreise_geo['features'][:10]])
    # 2. Die Karte bauen
    fig = px.choropleth(
        df,
        geojson=landkreise_geo,
        locations='landkreis',
        featureidkey='properties.krs_name_short', 
        color='status',
        color_continuous_scale=[[0, "white"], [1, "#006432"]],
        range_color=[0,1]
    )

    # 3. Karten-Einstellungen für Sichtbarkeit
    fig.update_geos(
    showlakes=True,
    showrivers=True,
    showcountries=True,
    resolution=50,
    fitbounds="geojson", # Zwingt Plotly, alles zu zeigen, was in der JSON steckt
    visible=True
)
    fig.update_traces(marker_line_width=0.5, marker_line_color="black")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_showscale=False)

    # Anzeige
    st.plotly_chart(fig, width='stretch')
    st.write("Stand: 03.04.2026, #spendenrudel")

st.markdown("---")
st.caption("Datenquellen: Landkreise GeoJSON von tb1978 via Kaggle | Visualisierung: #spendenrudel Dashboard")