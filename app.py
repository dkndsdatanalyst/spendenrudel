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

with open(file_name, 'r', encoding='utf-8-sig') as f:
    landkreise_geo = json.load(f)

# --- DEBUGGING: Zeige uns die verfügbaren Keys an ---
sample_feature = landkreise_geo['features'][0]['properties']
st.write("### Debug-Info: Keys in deiner GeoJSON")
st.write(sample_feature) # Hier siehst du alle verfügbaren Spaltennamen

# 2. Daten erstellen
# Wir extrahieren die Namen. WICHTIG: Prüfe hier, ob 'krs_name_short' wirklich existiert!
# Falls der Key in deiner Datei anders heißt (z.B. 'name'), ändere ihn hier:
key_name = 'krs_name_short' 

alle_namen = [f['properties'].get(key_name) for f in landkreise_geo['features'] if f['properties'].get(key_name)]
df = pd.DataFrame({'landkreis': alle_namen, 'status': 0.0})

# Wolfsburg suchen (flexibel)
df.loc[df['landkreis'].str.contains('Wolfsburg', case=False, na=False), 'status'] = 1.0

# 3. Karte zeichnen
try:
    fig = px.choropleth(
        df,
        geojson=landkreise_geo,
        locations='landkreis',
        featureidkey=f'properties.{key_name}', # Dynamischer Key
        color='status',
        color_continuous_scale=[[0, "#ffffff"], [1, "#006432"]],
        range_color=[0, 1],
        hover_name='landkreis'
    )

    fig.update_geos(
        visible=False, 
        fitbounds="geojson", 
        bgcolor="white"
    )
    
    # Dickere Linien, damit man die Umrisse überhaupt sieht
    fig.update_traces(marker_line_width=0.5, marker_line_color="#888")
    
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}, 
        coloraxis_showscale=False,
        height=600 # Feste Höhe für bessere Sichtbarkeit
    )

    st.plotly_chart(fig, use_container_width=True)

    # 4. Status-Check
    aktiviert = df[df['status'] > 0]['landkreis'].tolist()
    st.write(f"Gefundene Landkreise in der Liste: {len(df)}")
    if aktiviert:
        st.success(f"Aktiviert: {', '.join(aktiviert)}")
    else:
        st.warning("Wolfsburg wurde nicht gefunden. Schau oben in die Debug-Liste, wie es dort geschrieben wird!")

except Exception as e:
    st.error(f"Fehler beim Rendern: {e}")
