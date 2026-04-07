import streamlit as st
import pandas as pd
import pydeck as pdk
import json
import os

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #spendenrudel - Live Map")

GEOJSON_PATH = 'georef-germany-kreis.geojson'
ID_KEY = "krs_name_short"

# 1. Namen bereinigen
def clean_name(name):
    if pd.isna(name): return ""
    name = str(name).strip()
    replacements = [", Stadt", " Stadt", ", Hansestadt", " Hansestadt", "Landkreis ", "LK ", "Kreis "]
    for r in replacements:
        name = name.replace(r, "")
    return name.strip()

# 2. Daten laden (Hier später deine CSV einbinden)
raw_data = {
    'landkreis': ['Wolfsburg', 'Gifhorn', 'Berlin', 'Hannover'],
    'spenden_status': [1, 0, 0, 1]
}
df = pd.DataFrame(raw_data)
df['landkreis_clean'] = df['landkreis'].apply(clean_name)
# Set für schnelleren Abgleich
aktivierte_kreise = set(df[df['spenden_status'] > 0]['landkreis_clean'].tolist())

# 3. GeoJSON laden und Farben in Python berechnen
if not os.path.exists(GEOJSON_PATH):
    st.error(f"GeoJSON Datei '{GEOJSON_PATH}' fehlt!")
    st.stop()

@st.cache_data
def get_prepared_geojson(path, active_list):
    with open(path, 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    
    # Wir fügen jedem Feature direkt eine Farbe hinzu
    for feature in geojson['features']:
        name = feature['properties'].get(ID_KEY, "")
        # Abgleich mit dem Namen aus der GeoJSON (evtl. auch bereinigt)
        if name in active_list or clean_name(name) in active_list:
            feature['properties']['fill_color'] = [0, 100, 50, 200] # Grün
        else:
            feature['properties']['fill_color'] = [255, 255, 255, 150] # Weiß
    return geojson

# GeoJSON mit eingebackenen Farben holen
prepared_geo = get_prepared_geojson(GEOJSON_PATH, aktivierte_kreise)

# 4. Pydeck Layer (Greift jetzt nur noch auf den fertigen Wert zu)
geojson_layer = pdk.Layer(
    "GeoJsonLayer",
    prepared_geo, 
    opacity=0.8,
    stroked=True,
    filled=True,
    pickable=True,
    # Wir sagen Pydeck einfach: Nimm die Farbe, die schon in 'properties' steht
    get_fill_color="properties.fill_color", 
    get_line_color=[100, 100, 100],
    line_width_min_pixels=1,
)

view_state = pdk.ViewState(latitude=51.1657, longitude=10.4515, zoom=5.5)

r = pdk.Deck(
    layers=[geojson_layer],
    initial_view_state=view_state,
    map_style="light",
    tooltip={"html": "<b>Landkreis:</b> {properties." + ID_KEY + "}"}
)

st.pydeck_chart(r)

if aktivierte_kreise:
    st.success(f"Aktiviert: {', '.join(aktivierte_kreise)}")
