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
    with open('landkreise.json', encoding='utf-8') as f:
        landkreise_geo = json.load(f)
    
    with open('spender.csv', 'r', encoding='utf-8') as f:
        # Radikale Reinigung von Steuerzeichen
        content = "".join([line for line in f if line.strip()])
        df = pd.read_csv(io.StringIO(content))

    # Reinigung & Konvertierung
    df['landkreis'] = df['landkreis'].astype(str).str.strip()
    # Wir machen den Status zu Text ("0" oder "1"), um die Farben festzuzurren
    df['status'] = df['status'].astype(str).str.strip()

    # DIE FARBKARTE: 0 = Weiß/Grau, 1 = Wolfsburg-Grün
    color_map = {"0": "#f8f9fa", "1": "#006432"}

    fig = px.choropleth(
        df,
        geojson=landkreise_geo,
        locations='landkreis',
        featureidkey='properties.krs_name_short',
        color='status',
        color_discrete_map=color_map, # Hier wird die Farbe fest zugewiesen!
        category_orders={"status": ["0", "1"]}, # Reihenfolge erzwingen
        hover_name='landkreis'
    )

    fig.update_geos(
        visible=False,
        fitbounds="geojson",
        showcountries=False
    )
    
    fig.update_traces(
        marker_line_width=0.5, 
        marker_line_color="#444"
    )

    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        showlegend=False # Legende weg, damit es sauber aussieht
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # Kleiner Debugger für dich im Eiskeller:
    st.write("Gefundene Daten in der CSV:")
    st.dataframe(df)

st.markdown("---")
st.caption("Stand: 04.04.2026 | Spendenrudel Dashboard")
