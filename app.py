import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os

st.set_page_config(page_title="Spendenrudel Map Test", layout="wide")
st.title("🐺 #spendenrudel - Testmodus")

file_name = 'georef-germany-kreis.geojson'

# 1. Datei laden mit Fehlerprüfung
if not os.path.exists(file_name):
    st.error(f"❌ Datei '{file_name}' nicht gefunden!")
    st.stop()

try:
    with open(file_name, 'r', encoding='utf-8-sig') as f:
        raw_content = f.read()
        
    if not raw_content.strip():
        st.error(f"❌ Die Datei '{file_name}' ist komplett leer (0 Bytes).")
        st.stop()
        
    if "version https://git-lfs.github.com" in raw_content:
        st.error("❌ Git LFS Fehler! Deine App sieht nur den 'Pointer', nicht die echten Daten.")
        st.info("Lösung: Lade die Datei direkt bei GitHub hoch (Drag & Drop) statt über die Kommandozeile, oder deaktiviere LFS für diese Datei.")
        st.stop()

    landkreise_geo = json.loads(raw_content)

except Exception as e:
    st.error(f"❌ Kritischer Fehler beim Laden: {e}")
    st.stop()

# 2. Daten erstellen
# Wir nehmen den Namen aus der GeoJSON (Prüfe hier ggf. den Key 'krs_name_short')
features = landkreise_geo.get('features', [])
# Wir versuchen verschiedene Keys, falls krs_name_short nicht existiert
sample_props = features[0]['properties'] if features else {}
name_key = 'krs_name_short' if 'krs_name_short' in sample_props else next(iter(sample_props), None)

alle_namen = [f['properties'].get(name_key) for f in features if f['properties'].get(name_key)]
df = pd.DataFrame({'landkreis': alle_namen, 'status': 0.0})

# Wolfsburg aktivieren
df.loc[df['landkreis'].str.contains('Wolfsburg', case=False, na=False), 'status'] = 1.0

# 3. Karte zeichnen
try:
    fig = px.choropleth(
        df,
        geojson=landkreise_geo,
        locations='landkreis',
        featureidkey=f'properties.{name_key}',
        color='status',
        color_continuous_scale=[[0, "#ffffff"], [1, "#006432"]],
        range_color=[0, 1],
        hover_name='landkreis'
    )

    fig.update_geos(visible=False, fitbounds="geojson", bgcolor="white")
    fig.update_traces(marker_line_width=0.3, marker_line_color="#444")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_showscale=False)

    # Korrektur laut Log: width='stretch' statt use_container_width
    st.plotly_chart(fig, width='stretch')

    if not df[df['status'] > 0].empty:
        st.success(f"Aktiviert: {df[df['status'] > 0]['landkreis'].iloc[0]}")

except Exception as e:
    st.error(f"Fehler beim Rendern der Karte: {e}")

st.caption(f"Verwendeter Key aus GeoJSON: {name_key}")
