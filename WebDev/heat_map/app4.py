import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import random

# Generate random temperature data for locations in Tamil Nadu
num_points = 100
lats = np.random.uniform(low=8.1, high=13.8, size=num_points)  # Latitude range for Tamil Nadu
lons = np.random.uniform(low=76.9, high=80.3, size=num_points)  # Longitude range for Tamil Nadu
temps = np.random.uniform(low=40, high=70, size=num_points)  # Temperature in Fahrenheit

# Create a DataFrame
data = pd.DataFrame({
    'lat': lats,
    'lon': lons,
    'temperature': temps
})

# Define Pydeck HeatmapLayer
heatmap_layer = pdk.Layer(
    'HeatmapLayer',
    data=data,
    get_position='[lon, lat]',
    get_weight='temperature',  # Use temperature as the weight for the heatmap intensity
    radiusPixels=50,
    intensity=1,
    threshold=0.1
)

# Initial view of the map, centered on Tamil Nadu
initial_view = pdk.ViewState(
    latitude=11.0,
    longitude=78.0,
    zoom=6,
    pitch=50
)

# Render the deck.gl map
st.pydeck_chart(pdk.Deck(
    initial_view_state=initial_view,
    layers=[heatmap_layer],
    map_style='mapbox://styles/mapbox/dark-v10',
))
