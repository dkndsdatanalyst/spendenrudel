import streamlit as st
import pandas as pd
import pydeck as pdk
import json
import os

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #wobspendenrudel - Live Map")

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
    csv_path = 'spenden_status.csv' # Passe den Namen hier an
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        # Testdaten falls CSV noch nicht da/hochgeladen
        df = pd.DataFrame({
            'landkreis': ['Wolfsburg','Göttingen'],
            'spenden_status': [1, 1]
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

# --- 1. GEOJSON VORBEREITEN ---
geo_result = get_clean_geo(GEOJSON_PATH, aktiv_set)

# --- 2. STATISTIK-BERECHNUNG (HIER OBEN, DAMIT SIE ÜBERALL BEKANNT IST) ---
anzahl_aktiv = len(aktiv_set)
if isinstance(geo_result, dict) and 'features' in geo_result:
    anzahl_gesamt = len(geo_result['features'])
else:
    anzahl_gesamt = 401 # Fallback für Deutschland

# --- 3. KARTEN-DARSTELLUNG ---
if geo_result is None:
    st.error(f"Datei {GEOJSON_PATH} fehlt im Repository!")
elif geo_result == "LFS_ERROR":
    st.error("GitHub LFS Fehler: Die Datei wurde nicht korrekt hochgeladen.")
else:
    try:
        # Layer definieren
        layer = pdk.Layer(
            "GeoJsonLayer",
            geo_result,
            pickable=True,
            stroked=True,
            filled=True,
            get_fill_color="properties.fill_color",
            get_line_color=[150, 150, 150],
            line_width_min_pixels=1,
        )

        # Karte konfigurieren
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=pdk.ViewState(latitude=51.1, longitude=10.4, zoom=5.5),
            map_style="light",
            tooltip={"html": "<b>Landkreis:</b> {display_name}"}
        )

        # Karte NUR HIER EINMAL anzeigen
        st.pydeck_chart(r)

    except Exception as e:
        st.error(f"Darstellungsfehler: {e}")

ziel_gesamt = 194.5
th_aktuell = 9.45
fh_aktuell = 10

# --- 4. UNTERSCHRIFT & CREDITS (GANZ UNTEN) ---
st.markdown("---")

# 1. WICHTIG: Punkt statt Komma bei der Zahl!
ziel_gesamt = 194.5
th_aktuell = 9.45  # Auch hier Punkt nutzen
fh_aktuell = 10.0

# --- 4. UNTERSCHRIFT & CREDITS (GANZ UNTEN) ---
st.markdown("---")

# Die "1/xxx" Anzeige
st.subheader(f"📊 Fortschritt: {anzahl_aktiv} von {anzahl_gesamt} Landkreisen aktiv")
st.progress(anzahl_aktiv / anzahl_gesamt) # Korrigiert: Nur zwei 's' bei progress

# Tierheim-Balken
st.subheader(f"📊 Fortschritt: Tierheim-Spenden:") # Korrigiert: Anführungszeichen am Ende!
st.progress(th_aktuell / ziel_gesamt)

# Frauenhaus-Balken
st.subheader(f"📊 Fortschritt: Frauenhaus-Spenden:") # Korrigiert: Anführungszeichen am Ende!
st.progress(fh_aktuell / ziel_gesamt)

st.write("") # Kleiner Abstand
 
# Credits in zwei Spalten
col1, col2 = st.columns(2)
with col1:
    st.caption("✨ **Erstellt durch:** wobspendenrudel-intern")
with col2:
    st.caption("🗺️ **GEOJSON Quelle:** kaggle / tb1978")
