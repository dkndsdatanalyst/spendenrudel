import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
import os
import io

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #spendenrudel")

if not os.path.exists('landkreise.json') or not os.path.exists('landkreise.csv'):
    st.error("Dateien fehlen!")
else:
    with open('landkreise.json', encoding='utf-8') as f:
        landkreise_geo = json.load(f)
    
    try:
        # CSV laden
        df = pd.read_csv('landkreise.csv', sep=None, engine='python', encoding='utf-8-sig')
        
        # Dictionary für schnellen Zugriff: { 'wolfsburg': 1 }
        spenden_dict = dict(zip(
            df.iloc[:, 0].astype(str).str.strip().str.lower(), 
            df.iloc[:, 1].astype(float)
        ))

        # Listen für die Karte vorbereiten
        ids = []
        names = []
        z_values = []
        colors = []

        for feature in landkreise_geo['features']:
            name_raw = feature['properties'].get('krs_name_short', 'Unbekannt')
            clean_name = str(name_raw).strip().lower()
            
            status = spenden_dict.get(clean_name, 0.0)
            
            ids.append(name_raw)
            names.append(name_raw)
            z_values.append(status)
            # Manuelle Farbwahl: Grün für 1, Weiß für 0
            colors.append("#006432" if status > 0 else "#ffffff")

        # Die Karte mit Graph Objects bauen (stabiler als Express)
        fig = go.Figure(go.Choropleth(
            geojson=landkreise_geo,
            locations=ids,
            z=z_values,
            featureidkey="properties.krs_name_short",
            colorscale=[[0, "#ffffff"], [1, "#006432"]],
            showscale=False,
            marker_line_width=0.5,
            marker_line_color="#444",
            hovertemplate="<b>%{location}</b><extra></extra>"
        ))

        fig.update_geos(
            visible=False,
            fitbounds="geojson",
            bgcolor="white"
        )

        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            dragmode=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # Erfolgskontrolle
        if "wolfsburg" in spenden_dict:
            st.success(f"✅ Wolfsburg ist im System (Status {spenden_dict['wolfsburg']})")
        else:
            st.info("ℹ️ Wolfsburg nicht in der CSV gefunden. Check die Schreibweise!")

    except Exception as e:
        st.error(f"Fehler: {e}")

st.markdown("---")
st.caption("Modus: Manuelle Index-Steuerung (go.Choropleth)")
