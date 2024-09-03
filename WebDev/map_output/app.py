import streamlit as st
import requests
import pandas as pd
import json
import time
import pydeck as pdk

st.title("Real-time Temperature Map")

url = "http://127.0.0.1:5000/data"  # URL of the Flask server

# Initialize an empty DataFrame to store all location data
map_data = pd.DataFrame(columns=['lat', 'lon', 'temperature', 'color'])

# Define color scale based on temperature
def get_color(temperature):
    if temperature < 50:
        return [0, 0, 255]  # Blue for cooler temperatures
    elif temperature < 60:
        return [0, 255, 0]  # Green for moderate temperatures
    else:
        return [255, 0, 0]  # Red for warmer temperatures

# Initialize the map configuration with a zoomed-out view
initial_view = pdk.ViewState(latitude=11.0, longitude=78.0, zoom=6)  # Set initial zoom level

# Continuously fetch data and update map
response = requests.get(url, stream=True)
scatterplot_layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_data,
    get_position='[lon, lat]',
    get_fill_color='color',
    get_radius=5000,  # Adjusted radius for visibility
    pickable=True,  # Allows for tooltips
)
deck = pdk.Deck(
    initial_view_state=initial_view,
    layers=[scatterplot_layer],
    map_style='mapbox://styles/mapbox/dark-v10',
    tooltip={"text": "{temperature}°F at [{lat}, {lon}]"},
)
map_chart=st.pydeck_chart(deck)
for line in response.iter_lines():
    if line:
        try:
            # Decode the line and process it if it starts with "data:"
            decoded_line = line.decode('utf-8').strip()
            if decoded_line.startswith("data:"):
                json_data = decoded_line[5:]  # Strip off "data:" prefix
                data = json.loads(json_data)

                # Check if data is correctly formatted
                if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                    # Convert received data into a DataFrame
                    new_data = pd.DataFrame(data)
                    new_data['color'] = new_data['temperature'].apply(get_color)

                    # Replace old data with new data in map_data
                    map_data = new_data  # Overwrite map_data with new_data

                    # Update the scatterplot layer with the new data
                    scatterplot_layer.data=map_data
                    # Update the map chart with the modified layer
                    deck = pdk.Deck(
                        initial_view_state=initial_view,
                        layers=[scatterplot_layer],
                        map_style='mapbox://styles/mapbox/dark-v10',
                        tooltip={"text": "{temperature}°F at [{lat}, {lon}]"},
                    )
                    map_chart.pydeck_chart(deck)
                else:
                    st.error("Data format is incorrect.")
        except json.JSONDecodeError:
            st.error("Failed to decode JSON. Skipping this data point.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    # Optional: Add a small delay to control update rate
    time.sleep(1)
