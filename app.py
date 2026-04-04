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
    
    # 2. GeoJSON Keys säubern (Wir bauen uns einen sauberen Index)
    for feature in landkreise_geo['features']:
        # Wir nehmen den Namen und machen ihn "match-bereit" (klein, ohne Leerzeichen)
        raw_name = feature['properties'].get('krs_name_short', '')
        feature['properties']['clean_key'] = str(raw_name).strip().lower()

    # 3. CSV laden & ebenfalls radikal säubern
    with open('spender.csv', 'r', encoding='utf-8') as f:
        df_raw = pd.read_csv(io.StringIO(f.read().replace('\r', '').strip()))

    # Spaltennamen säubern (falls da Leerzeichen drin sind)
    df_raw.columns = df_raw.columns.str.strip().str.lower()
    
    # Den Landkreis-Namen in der CSV "match-bereit" machen
    df_raw['match_id'] = df_raw['landkreis'].astype(str).str.strip().lower()
    df_raw['status'] = pd.to_numeric(df_raw['status'], errors='coerce').fillna(0)

    # 4. Karte bauen
    fig = px.choropleth(
        df_raw,
        geojson=landkreise_geo,
        locations='match_id',           # Nutzt den gesäuberten Namen aus der CSV
        featureidkey='properties.clean_key', # Nutzt den gesäuberten Namen aus der JSON
        color='status',
        color_continuous_scale=[[0, "#ffffff"], [1, "#006432"]],
        range_color=[0, 1],
        hover_name='landkreis'
    )

    fig.update_geos(
        visible=False,
        fitbounds="geojson",
        showcountries=False,
        bgcolor="white"
    )
    
    # Wir machen die Linien mal richtig FETT und SCHWARZ, um zu sehen, ob überhaupt was gerendert wird
    fig.update_traces(
        marker_line_width=0.8, 
        marker_line_color="black"
    )

    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # --- DEBUG KONSOLE ---
    st.subheader("🛠️ Fehlersuche für Bruno:")
    col1, col2 = st.columns(2)
    with col1:
        st.write("In der CSV steht:")
        st.dataframe(df_raw[['landkreis', 'match_id', 'status']])
    with col2:
        st.write("Beispiele aus der Karte (JSON):")
        sample_names = [f['properties']['krs_name_short'] for f in landkreise_geo['features'][:5]]
        st.write(sample_names)
