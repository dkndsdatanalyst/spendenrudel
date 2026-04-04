import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os
import io

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #spendenrudel")

# 1. Dateien laden
if not os.path.exists('landkreise.json') or not os.path.exists('spender.csv'):
    st.error("Dateien fehlen!")
else:
    with open('landkreise.json', encoding='utf-8') as f:
        landkreise_geo = json.load(f)
    
    with open('spender.csv', 'r', encoding='utf-8') as f:
        df_raw = pd.read_csv(io.StringIO(f.read().replace('\r', '').strip()))

    # 2. DIE LÖSUNG: Wir bauen eine Liste ALLER Landkreise aus der GeoJSON
    all_districts = []
    for feature in landkreise_geo['features']:
        name = feature['properties'].get('krs_name_short')
        if name:
            all_districts.append(name)
    
    # Wir erstellen ein DataFrame mit allen 402 Landkreisen (Status 0 = Weiß)
    df_full = pd.DataFrame({'landkreis': all_districts, 'status': 0})

    # Jetzt überschreiben wir die Werte mit deinen echten Spenden-Daten
    for index, row in df_raw.iterrows():
        name = str(row['landkreis']).strip()
        val = pd.to_numeric(row['status'], errors='coerce')
        # Falls der Name in der Liste ist, setze den Status (z.B. 1 für Grün)
        df_full.loc[df_full['landkreis'] == name, 'status'] = val

    # Status als String für feste Farben (0=Weiß, 1=Grün)
    df_full['status'] = df_full['status'].astype(int).astype(str)

    # 3. Karte bauen
    fig = px.choropleth(
        df_full,
        geojson=landkreise_geo,
        locations='landkreis',
        featureidkey='properties.krs_name_short',
        color='status',
        color_discrete_map={"0": "#ffffff", "1": "#006432"}, # Festgenagelt!
        hover_name='landkreis',
        # Wir blenden die "0" (Weiß) im Hover aus, damit es sauber aussieht
        hover_data={'status': False} 
    )

    fig.update_geos(
        visible=False,
        fitbounds="geojson",
        bgcolor="rgba(0,0,0,0)" # Transparenter Hintergrund
    )
    
    fig.update_traces(marker_line_width=0.5, marker_line_color="#333")
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
    st.write(f"Vollständige Karte geladen. Landkreise gesamt: {len(df_full)}")

st.markdown("---")
st.caption("Status: Wolfsburg grün markiert, Rest Deutschland weiß.")
