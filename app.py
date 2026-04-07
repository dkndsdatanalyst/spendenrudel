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

# 2. Daten laden
raw_data = {
    'landkreis': ['Wolfsburg', 'Gifhorn', 'Berlin', 'Hannover'],
    'spenden_status': [1, 0, 0, 1]
}
df = pd.DataFrame(raw_data)
df['landkreis_clean'] = df['landkreis'].apply(clean_name)
aktivierte_kreise = df[df['spenden_status'] > 0]['landkreis_clean'].tolist()

# 3. GeoJSON laden
if not os.path.exists(GEOJSON_PATH):
    st.error("GeoJSON fehlt!")
    st.stop()

# 4. Pydeck Layer (Korrigierte Farblogik)
# Wir nutzen eine einfache IF-Bedingung in JavaScript-Syntax ohne das @@
geojson_layer = pdk.Layer(
    "GeoJsonLayer",
    GEOJSON_PATH,
    opacity=0.8,
    stroked=True,
    filled=True,
    pickable=True,
    # Diese Logik nutzt reines JavaScript, das Pydeck versteht:
    get_fill_color=f"properties.{ID_KEY} == 'Wolfsburg' || {json.dumps(aktivierte_kreise)}.includes(properties.{ID_KEY}) ? [0, 100, 50, 200] : [255, 255, 255, 150]",
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
