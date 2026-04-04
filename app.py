import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os
import io

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #spendenrudel")

if not os.path.exists('landkreise.json') or not os.path.exists('spender.csv'):
    st.error("Dateien fehlen im Repository!")
else:
    # 1. GeoJSON laden & Schlüssel säubern
    with open('landkreise.json', encoding='utf-8') as f:
        landkreise_geo = json.load(f)
    
    for feature in landkreise_geo['features']:
        name = feature['properties'].get('krs_name_short', 'unbekannt')
        feature['properties']['clean_key'] = str(name).strip().lower()

    # 2. CSV laden mit Schutz gegen unsichtbare Zeichen (BOM)
    with open('spender.csv', 'r', encoding='utf-8-sig') as f:
        content = f.read().replace('\r', '').strip()
    
    df = pd.read_csv(io.StringIO(content))

    # 3. Spaltennamen vereinheitlichen (Alles klein, Leerzeichen weg)
    df.columns = [c.strip().lower() for c in df.columns]

    # Check ob die Spalte da ist, sonst nehmen wir die erste Spalte als 'landkreis'
    target_col = 'landkreis' if 'landkreis' in df.columns else df.columns[0]
    status_col = 'status' if 'status' in df.columns else df.columns[1]

    # Daten für das Matching vorbereiten
    df['match_id'] = df[target_col].astype(str).str.strip().lower()
    df['val'] = pd.to_numeric(df[status_col], errors='coerce').fillna(0)

    # 4. Die Karte bauen
    fig = px.choropleth(
        df,
        geojson=landkreise_geo,
        locations='match_id',
        featureidkey='properties.clean_key',
        color='val',
        color_continuous_scale=[[0, "#ffffff"], [1, "#006432"]],
        range_color=[0, 1],
        hover_name=target_col
    )

    fig.update_geos(
        visible=False,
        fitbounds="geojson",
        showcountries=False,
        bgcolor="white"
    )
    
    fig.update_traces(
        marker_line_width=0.5, 
        marker_line_color="#444"
    )

    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # Debugger für Bruno (kannst du später löschen)
    with st.expander("🛠️ Debug-Daten anzeigen"):
        st.write("Spalten in deiner CSV:", list(df.columns))
        st.write("Daten-Vorschau:", df[['match_id', 'val']])
        st.write("Erste 5 Kreise in der Karte:", [f['properties']['clean_key'] for f in landkreise_geo['features'][:5]])

st.markdown("---")
st.caption("Stand: 04.04.2026 | #spendenrudel")
