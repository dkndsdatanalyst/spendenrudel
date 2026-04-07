import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os

st.set_page_config(page_title="Spendenrudel Map Test", layout="wide")
st.title("🐺 #spendenrudel - Testmodus")

# 1. GeoJSON laden
if not os.path.exists('georef-germany-kreis.geojson'):
    st.error("❌ Die 'landkreise.json' fehlt!")
    st.stop()

with open('georef-germany-kreis.geojson', 'r', encoding='utf-8-sig') as f:
    landkreise_geo = json.load(f)

# 2. Master-Liste im Speicher erstellen
# Wir ziehen alle Namen direkt aus der JSON
alle_namen = [f['properties'].get('krs_name_short') for f in landkreise_geo['features'] if f['properties'].get('krs_name_short')]
df = pd.DataFrame({'landkreis': alle_namen, 'status': 0.0})

# --- TEST-LOGIK: Wolfsburg auf 1 setzen ---
# Wir suchen "Wolfsburg" (ignoriere Groß/Klein) und setzen den Status auf 1
df.loc[df['landkreis'].str.strip().str.lower() == 'wolfsburg', 'status'] = 1.0

# 3. Karte zeichnen
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
        bgcolor="white"
    )
    
    fig.update_traces(marker_line_width=0.3, marker_line_color="#444")
    
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}, 
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # 4. Status-Check Text
    aktiviert = df[df['status'] > 0]['landkreis'].tolist()
    if aktiviert:
        st.success(f"Im Testmodus aktiviert: {', '.join(aktiviert)}")
    else:
        st.warning("Wolfsburg wurde in der Namensliste der JSON nicht gefunden!")

except Exception as e:
    st.error(f"Fehler beim Rendern: {e}")

st.markdown("---")
st.caption("Testmodus: Wolfsburg wird automatisch auf 1 gesetzt.")
