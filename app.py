import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os
import io

st.set_page_config(page_title="Spendenrudel Map", layout="wide")
st.title("🐺 #spendenrudel")

# 1. Dateien laden
if not os.path.exists('landkreise.json') or not os.path.exists('landkreise.csv'):
    st.error("Dateien fehlen im Repo! (landkreise.json & spender.csv)")
else:
    with open('landkreise.json', encoding='utf-8') as f:
        landkreise_geo = json.load(f)
    
    # 2. Master-Liste aus der GeoJSON erstellen
    # Wir ziehen alle Namen direkt aus der Quelle der Wahrheit
    master_data = []
    for feature in landkreise_geo['features']:
        name = feature['properties'].get('krs_name_short')
        if name:
            master_data.append(name)
    
    # Das ist unser "landkreise_komplett" Datensatz im Speicher
    landkreise_komplett = pd.DataFrame({'landkreis': master_data, 'status': 0.0})

    # 3. Deine spender.csv einlesen und die 1er setzen
    try:
        # Einlesen mit automatischer Trenner-Erkennung
        df_real = pd.read_csv('landkreise.csv', sep=None, engine='python', encoding='utf-8-sig')
        
        # Wir machen alles für den Vergleich kurz klein, damit "Wolfsburg" = "wolfsburg" ist
        landkreise_komplett['match_key'] = landkreise_komplett['landkreis'].str.strip().str.lower()
        
        # Spender-Daten säubern
        df_real['match_key'] = df_real.iloc[:, 0].astype(str).str.strip().str.lower()
        df_real['val'] = pd.to_numeric(df_real.iloc[:, 1], errors='coerce').fillna(0)

        # Die Werte von deiner CSV in die komplette Liste übertragen
        for _, row in df_real.iterrows():
            landkreise_komplett.loc[landkreise_komplett['match_key'] == row['match_key'], 'status'] = row['val']

        # 4. Die Karte zeichnen (jetzt mit dem kompletten Datensatz)
        fig = px.choropleth(
            landkreise_komplett,
            geojson=landkreise_geo,
            locations='landkreis',
            featureidkey='properties.krs_name_short',
            color='status',
            # Weiß (0) bis Wolfsburg-Grün (1)
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
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_showscale=False)

        st.plotly_chart(fig, use_container_width=True)

        # 5. Erfolgskontrolle im Interface
        found = landkreise_komplett[landkreise_komplett['status'] > 0]['landkreis'].tolist()
        if found:
            st.success(f"✅ Grün markiert: {', '.join(found)}")
        else:
            st.info("ℹ️ Aktuell sind alle Kreise weiß. (Check deine spender.csv!)")

    except Exception as e:
        st.error(f"Fehler beim Verarbeiten: {e}")

st.markdown("---")
st.caption("Modus: landkreise_komplett Sync aktiv.")
