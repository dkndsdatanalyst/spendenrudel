import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os

# --- APP KONFIGURATION ---
st.set_page_config(page_title="Spendenrudel Map Test", layout="wide")
st.title("🐺 #spendenrudel - Testmodus")

# --- 1. GEOJSON LADEN (mit Sicherheitscheck) ---
file_name = 'georef-germany-kreis.geojson'

if not os.path.exists(file_name):
    st.error(f"❌ Die Datei '{file_name}' fehlt im Verzeichnis!")
    st.stop()

try:
    with open(file_name, 'r', encoding='utf-8-sig') as f:
        # Wir lesen den Inhalt erst, um zu prüfen, ob er leer ist
        content = f.read()
        if not content.strip():
            st.error(f"⚠️ Die Datei '{file_name}' ist leer.")
            st.stop()
        
        # Falls es ein Git LFS Pointer ist, fängt dies den Fehler ab
        if "version https://git-lfs.github.com" in content:
            st.error("❌ Git LFS Fehler: Die GeoJSON-Datei wurde nicht korrekt heruntergeladen (nur der Pointer ist vorhanden).")
            st.stop()
            
        landkreise_geo = json.loads(content)
except json.JSONDecodeError as e:
    st.error(f"❌ JSON-Fehler beim Laden: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ Unerwarteter Fehler: {e}")
    st.stop()

# --- 2. DATEN AUFBEREITEN ---
# Wir ziehen alle Namen direkt aus der JSON
# Wir nutzen .get(), um Abstürze bei fehlenden Keys zu vermeiden
features = landkreise_geo.get('features', [])
alle_namen = [f['properties'].get('krs_name_short') for f in features if f['properties'].get('krs_name_short')]

if not alle_namen:
    st.error("❌ Keine Landkreise in der GeoJSON-Datei gefunden. Prüfe den Key 'krs_name_short'.")
    st.stop()

df = pd.DataFrame({'landkreis': alle_namen, 'status': 0.0})

# --- TEST-LOGIK: Wolfsburg auf 1 setzen ---
# Wir nutzen .str.contains, falls Wolfsburg Zusätze wie "Stadt" hat
mask = df['landkreis'].str.contains('Wolfsburg', case=False, na=False)
if mask.any():
    df.loc[mask, 'status'] = 1.0
else:
    st.warning("Wolfsburg wurde in der Liste der JSON nicht exakt gefunden!")

# --- 3. KARTE ZEICHNEN ---
try:
    fig = px.choropleth(
        df,
        geojson=landkreise_geo,
        locations='landkreis',
        featureidkey='properties.krs_name_short',
        color='status',
        # Farbskala: Weiß für 0, Wolfsburg-Grün für 1
        color_continuous_scale=[[0, "#ffffff"], [1, "#006432"]],
        range_color=[0, 1],
        hover_name='landkreis'
    )

    fig.update_geos(
        visible=False, 
        fitbounds="geojson", 
        bgcolor="rgba(0,0,0,0)" # Transparent
    )
    
    fig.update_traces(marker_line_width=0.3, marker_line_color="#444")
    
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}, 
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- 4. STATUS-CHECK TEXT ---
    aktiviert = df[df['status'] > 0]['landkreis'].tolist()
    if aktiviert:
        st.success(f"Im Testmodus aktiviert: {', '.join(aktiviert)}")

except Exception as e:
    st.error(f"Fehler beim Rendern der Karte: {e}")
    st.info("Hinweis: Prüfe, ob die 'locations' im DataFrame exakt mit den IDs im GeoJSON übereinstimmen.")

st.markdown("---")
st.caption("Testmodus: Wolfsburg wird automatisch auf 1 gesetzt. GeoJSON: " + file_name)
