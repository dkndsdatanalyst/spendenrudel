import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os
import io

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #spendenrudel")

if not os.path.exists('landkreise.json') or not os.path.exists('landkreise.csv'):
    st.error("Dateien fehlen!")
else:
    # 1. GeoJSON laden
    with open('landkreise.json', encoding='utf-8') as f:
        landkreise_geo = json.load(f)
    
    # 2. CSV laden
    try:
        df = pd.read_csv('landkreise.csv', sep=None, engine='python', encoding='utf-8-sig')
        # Wir machen ein Dictionary aus der CSV: { 'wolfsburg': 1, 'berlin': 0 }
        spenden_dict = dict(zip(
            df.iloc[:, 0].astype(str).str.strip().str.lower(), 
            df.iloc[:, 1].astype(float)
        ))

        # 3. DATEN DIREKT IN DIE GEOJSON SCHREIBEN (Der Trick!)
        for feature in landkreise_geo['features']:
            name = str(feature['properties'].get('krs_name_short', '')).strip().lower()
            # Wenn der Name in deiner Liste ist, kriegt er den Status, sonst 0
            feature['properties']['spende_status'] = spenden_dict.get(name, 0.0)

        # 4. Karte zeichnen (Wir nutzen jetzt die GeoJSON selbst als Datenquelle)
        fig = px.choropleth(
            geojson=landkreise_geo,
            locations=[f['properties']['krs_name_short'] for f in landkreise_geo['features']],
            featureidkey='properties.krs_name_short',
            color=[f['properties']['spende_status'] for f in landkreise_geo['features']],
            color_continuous_scale=[[0, "#ffffff"], [1, "#006432"]],
            range_color=[0, 1],
            labels={'color': 'Status'}
        )

        fig.update_geos(visible=False, fitbounds="geojson", bgcolor="white")
        fig.update_traces(marker_line_width=0.5, marker_line_color="#444")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_showscale=False)

        st.plotly_chart(fig, use_container_width=True)

        # Kleiner Monitor für dich
        if "wolfsburg" in spenden_dict:
            st.success(f"Wolfsburg erkannt! Status: {spenden_dict['wolfsburg']}")
        else:
            st.warning("Wolfsburg wurde in der CSV nicht gefunden (Check Schreibweise!)")

    except Exception as e:
        st.error(f"Fehler: {e}")

st.markdown("---")
st.caption("Status: Direkte GeoJSON-Injektion aktiv.")
