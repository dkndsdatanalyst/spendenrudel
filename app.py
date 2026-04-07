import streamlit as st
import pydeck as pdk
import json

st.set_page_config(layout="wide")
st.title("🐺 #spendenrudel - Pydeck Test")

# Pfad zur Datei
file_path = 'georef-germany-kreis.geojson'

# Initialer Status der Karte
view_state = pdk.ViewState(
    latitude=51.1657,
    longitude=10.4515,
    zoom=5,
    pitch=0
)

# Layer erstellen
layer = pdk.Layer(
    "GeoJsonLayer",
    file_path,
    opacity=0.8,
    stroked=True,
    filled=True,
    get_fill_color="[255, 255, 255]", # Standard: Weiß
    get_line_color=[100, 100, 100],
    line_width_min_pixels=1,
)

# Wolfsburg-Highlight Logik (Pydeck kann das direkt im Layer-Stil über JS-Strings)
# Hier wird geprüft, ob der Name "Wolfsburg" enthält -> dann Grün
layer.get_fill_color = "properties.krs_name_short == 'Wolfsburg' ? [0, 100, 50] : [255, 255, 255]"

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="light"
)

st.pydeck_chart(r)
