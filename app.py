import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os
import io

st.set_page_config(page_title="Spendenrudel Map", layout="wide")

# Titel & Style
st.markdown("<h1 style='text-align: center;'>🐺 #spendenrudel</h1>", unsafe_allow_html=True)

# 1. Sicherheits-Check
if not os.path.exists('landkreise.json') or not os.path.exists('spender.csv'):
    st.error("⚠️ Dateien fehlen im Repository!")
else:
    # 2. Daten laden
    with open('landkreise.json', encoding='utf-8') as f:
        landkreise_geo = json.load(f)
    
    # CSV laden & säubern
    with open('spender.csv', 'r', encoding='utf-8') as f:
        df = pd.read_csv(io.StringIO(f.read().replace('\r', '').strip()))

    # 3. Das "Sorglos-Matching"
    # Wir machen alles klein und entfernen "Stadt"/"Landkreis" für den Vergleich
    df['match_name'] = df['landkreis'].str.lower().str.replace('landkreis', '', case=False).str.replace('stadt', '', case=False).str.strip()
    df['status'] = pd.to_numeric(df['status'], errors='coerce').fillna(0)

    for feature in landkreise_geo['features']:
        orig_name = feature['properties'].get('krs_name_short', '')
        feature['properties']['match_key'] = orig_name.lower().replace('landkreis', '').replace('stadt', '').strip()

    # 4. Die Karte bauen
    fig = px.choropleth(
        df,
        geojson=landkreise_geo,
        locations='match_name',
        featureidkey='properties.match_key',
        color='status',
        # Von Weiß (0) zu Wolfsburg-Grün (1)
        color_continuous_scale=[[0, "#f8f9fa"], [1, "#006432"]],
        range_color=[0, 1],
        hover_data={'match_name': False, 'landkreis': True, 'status': False}
    )

    # 5. Geometrie & Layout optimieren
    fig.update_geos(
        visible=False,
        fitbounds="geojson", # Zwingt den Zoom auf ganz Deutschland
    )
    
    fig.update_traces(
        marker_line_width=0.5, 
        marker_line_color="#444" # Dunkelgraue Grenzen für bessere Sichtbarkeit
    )
    
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_showscale=False,
        dragmode=False # Fixiert die Karte für Mobile-User
    )

    # 6. Anzeige
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"<p style='text-align: center; color: gray;'>Stand: {pd.Timestamp.now().strftime('%d.%m.%p')} | #spendenrudel</p>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Daten: Landkreise GeoJSON | Visualisierung: Spendenrudel Dashboard")
