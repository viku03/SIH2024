import streamlit as st
import pandas as pd
import pydeck as pdk
import requests
import json

# SSE URL
sse_url ="http://127.0.0.1:5000/data"  # Replace with your Flask server's URL

# Function to fetch data from the SSE stream
def get_temperature_data():
    response = requests.get(sse_url, stream=True)
    
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith('data:'):
                # Parse the JSON data from SSE
                data = json.loads(decoded_line[5:])
                return pd.DataFrame(data)  # Return as pandas DataFrame

# Title
st.title("Real-Time Temperature Heatmap")

# Manual refresh button
if st.button('Refresh Data'):
    # Fetch new data when button is clicked
    data = get_temperature_data()
else:
    # Load data initially
    data = get_temperature_data()

# Check if data is available
if data is not None:
    # Normalize temperature values for heatmap intensity
    data['temperature_intensity'] = data['temperature'] / data['temperature'].max()

    # Define a heatmap layer
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data,
        get_position='[lon, lat]',
        get_weight='temperature_intensity',  # Use temperature intensity for heatmap
        radius_pixels=60,
        intensity=1,
        threshold=0.1,
        opacity = 0.4
    )

    # Set the initial view state (centered around Tamil Nadu)
    view_state = pdk.ViewState(
        latitude=10.9,  # Center of Tamil Nadu
        longitude=78.7,
        zoom=6,
        pitch=0
    )

    # Render the map with the heatmap layer
    st.pydeck_chart(pdk.Deck(
        layers=[heatmap_layer],
        initial_view_state=view_state,
        # Use a Mapbox style with a white background and black borders
        map_style='mapbox://styles/mapbox/light-v9',  # Or use a custom style
        parameters={"clearColor": [255, 255, 255, 1]},  # Set the background to white
    ))
else:
    st.error("No data available.")
