import streamlit as st
import plotly.express as px
import pandas as pd
import json
import io

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #spendenrudel")

# 1. Daten laden
try:
    with open('landkreise.json', encoding='utf-8') as f:
        landkreise_geo = json.load(f)

    with open('spender.csv', 'r', encoding='utf-8') as f:
        # Säubern von unsichtbaren Zeichen (\r)
        raw_csv = f.read().replace('\r', '').strip()
        df = pd.read_csv(io.StringIO(raw_csv))

    # --- MATCHING LOGIK (Der Retter) ---
    # Wir erstellen in der CSV einen "Clean-Namen": klein & ohne "stadt"/"landkreis"
    df['landkreis_clean'] = df['landkreis'].str.lower().str.replace('landkreis', '', case=False).str.replace('stadt', '', case=False).str.strip()
    df['status'] = pd.to_numeric(df['status'], errors='coerce').fillna(0)

    # Wir machen das Gleiche für jedes Element in der GeoJSON
    for feature in landkreise_geo['features']:
        name_in_json = feature['properties'].get('krs_name_short', '')
        # Wir speichern einen neuen Key "match_key" direkt im GeoJSON-Objekt
        feature['properties']['match_key'] = name_in_json.lower().replace('landkreis', '').replace('stadt', '').strip()

    # 2. Die Karte bauen
    fig = px.choropleth(
        df,
        geojson=landkreise_geo,
        locations='landkreis_clean',     # Nutzt den gesäuberten Namen aus der CSV
        featureidkey='properties.match_key', # Vergleicht mit dem gesäuberten Namen in der JSON
        color='status',
        color_continuous_scale=[[0, "white"], [1, "#006432"]],
        range_color=[0, 1]
    )

    # 3. Karten-Ansicht optimieren
    fig.update_geos(
        visible=False, 
        fitbounds="geojson" # Zeigt IMMER ganz Deutschland, egal wer grün ist
    )
    
    fig.update_traces(marker_line_width=0.5, marker_line_color="gray")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_showscale=False)

    # 4. Ausgabe
    st.plotly_chart(fig, width='stretch')
    st.write(f"Stand: 03.04.2026 | Aktive Landkreise: {len(df[df['status'] > 0])}")

except Exception as e:
    st.error(f"Fehler beim Laden: {e}")

st.markdown("---")
st.caption("Visualisierung: #spendenrudel Dashboard")