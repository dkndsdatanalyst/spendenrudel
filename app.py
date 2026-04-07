import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os

st.set_page_config(page_title="Spendenrudel Map Test", layout="wide")
st.title("🐺 #spendenrudel - Testmodus")

file_name = 'georef-germany-kreis.geojson'

# 1. GeoJSON laden
if not os.path.exists(file_name):
    st.error(f"❌ Datei '{file_name}' fehlt!")
    st.stop()

try:
    with open(file_name, 'r', encoding='utf-8') as f:
        landkreise_geo = json.load(f)

    # --- AUTOMATISCHE KEY-SUCHE ---
    # Wir schauen uns das erste Element an, um zu sehen, wie die Spalte für den Namen heißt
    first_props = landkreise_geo['features'][0]['properties']
    
    # Mögliche Keys für den Landkreisnamen in solchen Dateien
    possible_keys = ['krs_name_short', 'name_2', 'name', 'GEN', 'lan_name_short']
    name_key = next((k for k in possible_keys if k in first_props), None)

    if not name_key:
        # Falls keiner der Keys passt, nehmen wir den ersten verfügbaren Key
        name_key = list(first_props.keys())[0]

    # 2. DataFrame erstellen
    # Wir extrahieren alle Namen exakt so, wie sie in der GeoJSON stehen
    alle_namen_aus_json = [f['properties'][name_key] for f in landkreise_geo['features'] if name_key in f['properties']]
    
    df = pd.DataFrame({'landkreis_id': alle_namen_aus_json, 'status': 0.0})

    # Wolfsburg aktivieren (Suche nach Teilstring "Wolfsburg")
    df.loc[df['landkreis_id'].str.contains('Wolfsburg', case=False, na=False), 'status'] = 1.0

    # 3. Karte zeichnen
    fig = px.choropleth(
        df,
        geojson=landkreise_geo,
        locations='landkreis_id',          # Spalte im DataFrame
        featureidkey=f'properties.{name_key}', # Pfad in der GeoJSON
        color='status',
        color_continuous_scale=[[0, "#ffffff"], [1, "#006432"]],
        range_color=[0, 1],
        hover_name='landkreis_id'
    )

    fig.update_geos(
        visible=False, 
        fitbounds="geojson", 
        bgcolor="white"
    )
    
    fig.update_traces(marker_line_width=0.2, marker_line_color="#444")
    
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}, 
        coloraxis_showscale=False,
        height=700
    )

    st.plotly_chart(fig, width='stretch')

    # Status-Anzeige unter der Karte
    aktiviert = df[df['status'] > 0]['landkreis_id'].tolist()
    if aktiviert:
        st.success(f"Aktiviert: {aktiviert[0]}")
    else:
        st.warning(f"Wolfsburg wurde nicht gefunden. In der JSON genutzter Key: '{name_key}'")

except Exception as e:
    st.error(f"Fehler beim Verarbeiten: {e}")

st.markdown("---")
st.caption(f"Debug: Nutze Spalte '{name_key}' aus der GeoJSON für die Zuordnung.")
