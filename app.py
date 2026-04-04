import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #spendenrudel")

# 1. Dateien laden
if not os.path.exists('landkreise.json'):
    st.error("❌ Die 'landkreise.json' fehlt im Repository!")
    st.stop()

with open('landkreise.json', 'r', encoding='utf-8-sig') as f:
    landkreise_geo = json.load(f)

# 2. Automatische Erstellung der Vorlage (falls keine CSV da ist)
if not os.path.exists('landkreise.csv'):
    st.info("💡 Erstelle neue landkreise.csv Vorlage...")
    alle_namen = [f['properties'].get('krs_name_short') for f in landkreise_geo['features'] if f['properties'].get('krs_name_short')]
    # Alphabetisch sortieren für bessere Übersicht in Excel
    alle_namen.sort()
    df_template = pd.DataFrame({'landkreis': alle_namen, 'status': 0})
    df_template.to_csv('landkreise.csv', index=False, encoding='utf-8-sig')
    st.success("✅ Datei 'landkreise.csv' wurde erstellt. Bitte lade sie herunter, bearbeite sie und lade sie wieder hoch.")

# 3. Die CSV einlesen (deine Arbeitsdatei)
try:
    df = pd.read_csv('landkreise.csv', encoding='utf-8-sig')
    
    # 4. Karte zeichnen
    fig = px.choropleth(
        df,
        geojson=landkreise_geo,
        locations='landkreis',
        featureidkey='properties.krs_name_short',
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
    
    fig.update_traces(marker_line_width=0.4, marker_line_color="#444")
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}, 
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Anzeige der aktivierten Kreise
    aktiviert = df[df['status'] > 0]['landkreis'].tolist()
    if aktiviert:
        st.success(f"Aktiviert: {', '.join(aktiviert)}")

except Exception as e:
    st.error(f"Fehler beim Lesen der landkreise.csv: {e}")
