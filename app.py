import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os
import io

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #spendenrudel")

if not os.path.exists('landkreise.json') or not os.path.exists('landkreise.csv'):
    st.error("Dateien fehlen im Repository!")
else:
    # 1. GeoJSON laden & Schlüssel säubern
    with open('landkreise.json', encoding='utf-8') as f:
        landkreise_geo = json.load(f)
    
    for feature in landkreise_geo['features']:
        name = feature['properties'].get('krs_name_short', 'unbekannt')
        feature['properties']['clean_key'] = str(name).strip().lower()

    # 2. CSV laden mit automatischer Trennzeichen-Erkennung
    try:
        # sep=None + engine='python' erkennt automatisch ob Komma oder Semikolon
        df = pd.read_csv('landkreise.csv', sep=None, engine='python', encoding='utf-8-sig')
        
        # FIX: .str.lower() statt nur .lower()
        df['match_id'] = df.iloc[:, 0].astype(str).str.strip().str.lower()
        df['val'] = pd.to_numeric(df.iloc[:, 1], errors='coerce').fillna(0)

        # 3. Die Karte bauen
        fig = px.choropleth(
            df,
            geojson=landkreise_geo,
            locations='match_id',
            featureidkey='properties.clean_key',
            color='val',
            color_continuous_scale=[[0, "#ffffff"], [1, "#006432"]],
            range_color=[0, 1],
            hover_name=df.columns[0]
        )

        fig.update_geos(
            visible=False,
            fitbounds="geojson",
            showcountries=False,
            bgcolor="white"
        )
        
        fig.update_traces(marker_line_width=0.5, marker_line_color="#444")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_showscale=False)

        st.plotly_chart(fig, use_container_width=True)

        # DEBUG-BEREICH
        with st.expander("🛠️ Debug-Check"):
            st.write("Match-Liste aus CSV:", df['match_id'].tolist())
            st.write("Erste 3 aus GeoJSON:", [f['properties']['clean_key'] for f in landkreise_geo['features'][:3]])

    except Exception as e:
        st.error(f"Kritischer Fehler: {e}")

st.markdown("---")
st.caption("Stand: 04.04.2026 | #spendenrudel")
