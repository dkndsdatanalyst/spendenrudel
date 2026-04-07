import streamlit as st
import pandas as pd
import pydeck as pdk
import json
import os

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #spendenrudel - Live Map")

# --- KONFIGURATION ---
GEOJSON_PATH = 'georef-germany-kreis.geojson'
ID_KEY = "krs_name_short"  # Der Key aus deiner GeoJSON

# --- 1. HILFSFUNKTION: NAMEN BEREINIGEN ---
def clean_name(name):
    if pd.isna(name):
        return ""
    name = str(name)
    # Häufige Zusätze entfernen, die in 'krs_name_short' meist nicht vorkommen
    replacements = [
        ", Stadt", " Stadt", ", Hansestadt", " Hansestadt",
        "Landkreis ", "LK ", "Kreis ", " lkr."
    ]
    for r in replacements:
        name = name.replace(r, "")
    
    # Leerzeichen am Anfang/Ende weg und Klammern vereinheitlichen
    return name.strip()

# --- 2. DATEN LADEN & BEREINIGEN ---
@st.cache_data
def load_and_clean_data():
    # Falls du eine CSV hast: df = pd.read_csv('spenden.csv')
    # Hier als Beispiel ein DataFrame:
    raw_data = {
        'landkreis': ['Wolfsburg, Stadt', 'LK Gifhorn', 'Berlin', 'Region Hannover'],
        'spenden_status': [1, 0, 0, 1]
    }
    df = pd.DataFrame(raw_data)
    
    # Bereinigung anwenden
    df['landkreis_clean'] = df['landkreis'].apply(clean_name)
    return df

df = load_and_clean_data()

# Liste der aktivierten Landkreise (Status > 0)
aktivierte_kreise = df[df['spenden_status'] > 0]['landkreis_clean'].tolist()

# --- 3. GEOJSON LADEN ---
if not os.path.exists(GEOJSON_PATH):
    st.error(f"GeoJSON '{GEOJSON_PATH}' fehlt!")
    st.stop()

# --- 4. PYDECK MAP ---
geojson_layer = pdk.Layer(
    "GeoJsonLayer",
    GEOJSON_PATH,
    opacity=0.8,
    stroked=True,
    filled=True,
    # Logik: Ist der Name aus der GeoJSON in unserer 'aktivierte_kreise' Liste?
    get_fill_color=f"@@= {json.dumps(aktivierte_kreise)}.includes(properties.{ID_KEY}) ? [0, 100, 50, 200] : [255, 255, 255, 150]",
    get_line_color=[100, 100, 100],
    line_width_min_pixels=1,
    pickable=True,
)

view_state = pdk.ViewState(latitude=51.1657, longitude=10.4515, zoom=5.5)

r = pdk.Deck(
    layers=[geojson_layer],
    initial_view_state=view_state,
    map_style="light",
    tooltip={"html": f"<b>Landkreis:</b> {{properties.{ID_KEY}}}"}
)

st.pydeck_chart(r)

# --- 5. ÜBERSICHT ---
col1, col2 = st.columns(2)
with col1:
    st.write("### Rohdaten aus CSV")
    st.dataframe(df[['landkreis', 'spenden_status']])

with col2:
    st.write("### Bereinigte Namen für Map-Matching")
    st.dataframe(df[['landkreis_clean', 'spenden_status']])

if aktivierte_kreise:
    st.success(f"Gefundene Treffer auf der Karte: {', '.join(aktivierte_kreise)}")
