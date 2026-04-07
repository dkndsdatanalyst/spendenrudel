import streamlit as st
import pandas as pd
import pydeck as pdk
import json
import os

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #spendenrudel - Live Map")

GEOJSON_PATH = 'georef-germany-kreis.geojson'
# Wir nutzen diesen Key nur für den Tooltip
ID_KEY = "krs_name_short"

# 1. Namen bereinigen
def clean_name(name):
    if pd.isna(name): return ""
    name = str(name).strip()
    for r in [", Stadt", " Stadt", ", Hansestadt", " Land", "Landkreis ", "LK ", "Kreis "]:
        name = name.replace(r, "")
    return name.strip()

# 2. Daten laden
# Ersetze dies durch: df = pd.read_csv('deine_datei.csv')
raw_data = {'landkreis': ['Wolfsburg', 'Berlin'], 'status': [1, 0]}
df = pd.DataFrame(raw_data)
df['clean'] = df['landkreis'].apply(clean_name)
aktiv_set = set(df[df['status'] > 0]['clean'].tolist())

# 3. GeoJSON laden und "Säubern"
if not os.path.exists(GEOJSON_PATH):
    st.error("Datei fehlt!")
    st.stop()

@st.cache_data
def get_clean_geo(path, active_names):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for feature in data['features']:
        # Wir holen uns den Namen
        prop_name = feature['properties'].get(ID_KEY, "")
        
        # WICHTIG: Wir löschen ALLE anderen Properties, die den Fehler 
        # ".i" oder "Variable starts with number" verursachen könnten!
        name_for_tooltip = str(prop_name)
        feature['properties'] = {'display_name': name_name_for_tooltip}
        
        # Farbe setzen
        if clean_name(prop_name) in active_names:
            feature['properties']['fill_color'] = [0, 100, 50, 200]
        else:
            feature['properties']['fill_color'] = [255, 255, 255, 140]
            
    return data

# GeoJSON vorbereiten
clean_geo = get_clean_geo(GEOJSON_PATH, aktiv_set)

# 4. Pydeck Layer
# Wir benutzen jetzt NUR NOCH die Felder, die wir selbst angelegt haben
layer = pdk.Layer(
    "GeoJsonLayer",
    clean_geo,
    pickable=True,
    stroked=True,
    filled=True,
    extrude=False,
    get_fill_color="properties.fill_color", # Unser eigenes Feld
    get_line_color=[150, 150, 150],
    line_width_min_pixels=1,
)

view_state = pdk.ViewState(latitude=51.1, longitude=10.4, zoom=5.5)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="light",
    tooltip={"html": "<b>Landkreis:</b> {display_name}"} # Unser eigenes Feld
)

st.pydeck_chart(r)

if aktiv_set:
    st.success(f"Aktiviert: {', '.join(aktiv_set)}")
