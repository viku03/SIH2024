import streamlit as st
import pydeck as pdk
import json

# Load the GeoJSON data for Tamil Nadu
# Replace 'tamil_nadu.geojson' with the path to your actual GeoJSON file
with open("D:\Downloads\TamilNadu.geojson") as f:
    geojson_data = json.load(f)

# Define the GeoJsonLayer to shade Tamil Nadu
geojson_layer = pdk.Layer(
    "GeoJsonLayer",
    geojson_data,
    stroked=False,  # Do not outline the region (if you prefer)
    filled=True,  # Fill the state region
    get_fill_color=[0, 128, 255, 180],  # Specify the color in RGBA (this will fill with blue)
    get_line_color=[255, 255, 255],  # Line color (optional) to outline the border
    line_width_min_pixels=1,
)

# Set the initial view state (centered around Tamil Nadu)
view_state = pdk.ViewState(
    latitude=10.9,  # Center of Tamil Nadu
    longitude=78.7,
    zoom=6,
    pitch=0  # Top-down view
)

# Render the map with the GeoJson layer to color Tamil Nadu
st.pydeck_chart(pdk.Deck(
    layers=[geojson_layer],
    initial_view_state=view_state,
    map_style='mapbox://styles/mapbox/light-v9',  # Choose a suitable Mapbox style
))
