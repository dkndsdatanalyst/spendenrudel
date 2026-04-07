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
    name = str(name)
    for r in [", Stadt", " Stadt", ", Hansestadt", " Hansestadt", "Landkreis ", "LK ", "Kreis "]:
        name = name.replace(r, "")
    return name.strip()

# 2. Daten vorbereiten
raw_data = {
    'landkreis': ['Wolfsburg', 'Gifhorn', 'Berlin', 'Hannover'],
    'spenden_status': [1, 0, 0, 1]
}
df = pd.DataFrame(raw_data)
df['landkreis_clean'] = df['landkreis'].apply(clean_name)
aktivierte_kreise = set(df[df['spenden_status'] > 0]['landkreis_clean'].tolist())

# 3. GeoJSON laden und Farben in Python berechnen
if not os.path.exists(GEOJSON_PATH):
    st.error("GeoJSON fehlt!")
    st.stop()

with open(GEOJSON_PATH, 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

# Wir fügen jedem Feature direkt eine Farbe hinzu
for feature in geojson_data['features']:
    name = feature['properties'].get(ID_KEY, "")
    # Check ob der Name (oder bereinigte Name) in unseren aktiven Kreisen ist
    if name in aktivierte_kreise or clean_name(name) in aktivierte_kreise:
        feature['properties']['fill_color'] = [0, 100, 50, 200] # Grün
    else:
        feature['properties']['fill_color'] = [255, 255, 255, 150] # Weiß

# 4. Pydeck Layer (Greift jetzt nur noch auf den fertigen Wert zu)
geojson_layer = pdk.Layer(
    "GeoJsonLayer",
    geojson_data, # Wir übergeben das bearbeitete Objekt statt des Pfads
    opacity=0.8,
    stroked=True,
    filled=True,
    pickable=True,
    get_fill_color="properties.fill_color", # Direkter Zugriff auf den berechneten Wert
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
