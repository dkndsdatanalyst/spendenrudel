import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #spendenrudel")

# Check ob Dateien da sind
if not os.path.exists('landkreise.json') or not os.path.exists('spender.csv'):
    st.error("Dateien fehlen! Bitte landkreise.json und spender.csv im Ordner anlegen.")
else:
    # Daten laden
    with open('landkreise.json', encoding='utf-8') as f:
        landkreise_geo = json.load(f)
    
    df = pd.read_csv('spender.csv')

    # Karte bauen
    fig = px.choropleth(
        df,
        geojson=landkreise_geo,
        locations='landkreis',
        featureidkey='properties.krs_name_short', # <--- DAS HIER ANPASSEN
        color='status',
        color_continuous_scale=[[0, "white"], [1, "#006432"]],
        range_color=[0, 1]
    )

    fig.update_geos(visible=False, fitbounds="locations")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_showscale=False)

    st.plotly_chart(fig, use_container_width=True)
    st.write("Stand: 03.04.2026, #spendenrudel")

    st.markdown("---")
st.caption("Datenquellen: Landkreise GeoJSON von tb1978 via Kaggle | "
           "Visualisierung: #spendenrudel Dashboard")