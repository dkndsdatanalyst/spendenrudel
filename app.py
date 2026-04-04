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
        df_raw = pd.read_csv(io.StringIO(f.read().replace('\r', '').strip()))

    # 1. Alle Landkreise aus der GeoJSON ziehen
    all_districts = [f['properties']['krs_name_short'] for f in landkreise_geo['features']]
    df_full = pd.DataFrame({'landkreis': all_districts, 'status': 0.0}) # Wichtig: Float für die Skala

    # 2. Deine Spenden-Daten drüberbügeln
    for _, row in df_raw.iterrows():
        name = str(row['landkreis']).strip()
        val = float(row['status'])
        df_full.loc[df_full['landkreis'] == name, 'status'] = val

    # 3. Die Karte bauen mit einer KONTINUIERLICHEN Skala (Sicherer gegen White-Out)
    fig = px.choropleth(
        df_full,
        geojson=landkreise_geo,
        locations='landkreis',
        featureidkey='properties.krs_name_short',
        color='status',
        # Wir zwingen Plotly: Alles bei 0 ist Weiß, alles bei 1 ist sattes Grün
        color_continuous_scale=[[0, "#ffffff"], [1, "#006432"]],
        range_color=[0, 1],
        hover_name='landkreis'
    )

    # 4. Optik-Feinschliff
    fig.update_geos(
        visible=False,
        fitbounds="geojson",
        bgcolor="rgba(0,0,0,0)"
    )
    
    # Dickere Linien, damit man die Umrisse IMMER sieht
    fig.update_traces(
        marker_line_width=1.0, 
        marker_line_color="#444444"
    )

    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_showscale=False # Wir brauchen den hässlichen Balken an der Seite nicht
    )

    # 5. Anzeige
    st.plotly_chart(fig, use_container_width=True)
    
    # Kleiner Monitor für Bruno
    st.write(f"Vollständige Karte geladen. Landkreise gesamt: {len(df_full)}")
    st.write("Grüne Landkreise:", df_full[df_full['status'] > 0]['landkreis'].tolist())

st.markdown("---")
st.caption("Visualisierung: #spendenrudel Dashboard")
