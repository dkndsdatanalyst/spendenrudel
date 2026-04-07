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
    # Entfernt gängige Zusätze für besseres Matching
    for r in [", Stadt", " Stadt", ", Hansestadt", " Hansestadt", "Landkreis ", "LK ", "Kreis "]:
        name = name.replace(r, "")
    return name.strip()

# 2. Daten laden (CSV Einbindung)
@st.cache_data
def load_spenden_data():
    # Falls die Datei existiert, lade sie. Sonst nimm Testdaten.
    csv_path = 'spenden.csv' # Passe den Namen hier an
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        # Testdaten falls CSV noch nicht da/hochgeladen
        df = pd.DataFrame({
            'landkreis': ['Wolfsburg', 'Gifhorn', 'Berlin'],
            'spenden_status': [1, 0, 0]
        })
    
    df['clean'] = df['landkreis'].apply(clean_name)
    return df

df_spenden = load_spenden_data()
aktiv_set = set(df_spenden[df_spenden['spenden_status'] > 0]['clean'].tolist())

# 3. GeoJSON laden und "Säubern" (Hier war der NameError)
if not os.path.exists(GEOJSON_PATH):
    st.error(f"GeoJSON Datei '{GEOJSON_PATH}' fehlt!")
    st.stop()

@st.cache_data
def get_clean_geo(path, active_names):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for feature in data['features']:
        # Originalnamen sichern
        prop_name = feature['properties'].get(ID_KEY, "Unbekannt")
        
        # RADIKAL-REINIGUNG: Wir überschreiben alle Properties, 
        # um den ".i" Fehler durch Zahlen am Spaltenanfang zu verhindern.
        name_for_tooltip = str(prop_name)
        
        # Farbe bestimmen
        if clean_name(prop_name) in active_names:
            fill = [0, 100, 50, 200] # Grün
        else:
            fill = [255, 255, 255, 140] # Weiß
            
        # Nur diese zwei Felder darf Pydeck sehen:
        feature['properties'] = {
            'display_name': name_for_tooltip,
            'fill_color': fill
        }
            
    return data

# GeoJSON vorbereiten
try:
    clean_geo = get_clean_geo(GEOJSON_PATH, aktiv_set)

    # 4. Pydeck Layer
    layer = pdk.Layer(
        "GeoJsonLayer",
        clean_geo,
        pickable=True,
        stroked=True,
        filled=True,
        get_fill_color="properties.fill_color",
        get_line_color=[150, 150, 150],
        line_width_min_pixels=1,
    )

    view_state = pdk.ViewState(latitude=51.1, longitude=10.4, zoom=5.5)

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="light",
        tooltip={"html": "<b>Landkreis:</b> {display_name}"}
    )

    st.pydeck_chart(r)
    # ... (vorheriger Code mit st.pydeck_chart(r))
    st.pydeck_chart(r)

except Exception as e:
    st.error(f"Darstellungsfehler: {e}")

# --- AB HIER: Statistik & Unterschrift (Außerhalb des try-Blocks) ---
st.markdown("---")

# Dynamische Zählung
anzahl_aktiv = len(aktiv_set)
# Wir zählen die Features in der GeoJSON für die Gesamtzahl
anzahl_gesamt = len(geo_result['features']) if isinstance(geo_result, dict) else 400

# Die Anzeige
st.subheader(f"📊 Fortschritt: {anzahl_aktiv} von {anzahl_gesamt} Landkreisen aktiv")
st.progress(anzahl_aktiv / anzahl_gesamt)

st.write("") # Kleiner Abstand

# Credits & Quellen in Spalten
col1, col2 = st.columns(2)
with col1:
    st.caption("✨ **Erstellt durch:** wobspendenrudel-intern")
with col2:
    st.caption("🗺️ **GEOJSON Quelle:** kaggle / tb1978")
