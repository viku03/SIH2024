import streamlit as st
import requests
import pandas as pd
import json
import time
import pydeck as pdk

st.title("Real-time Temperature Heatmap")

url = "http://127.0.0.1:5000/data"  # URL of the Flask server

# Initialize an empty DataFrame to store all location data
map_data = pd.DataFrame(columns=['lat', 'lon', 'temperature'])

# Initialize the map configuration with a zoomed-out view
initial_view = pdk.ViewState(latitude=11.0, longitude=78.0, zoom=6)

# HeatmapLayer
def get_heatmap_layer(data):
    return pdk.Layer(
        "HeatmapLayer",
        data=data,
        get_position='[lon, lat]',  # Specify the latitude and longitude
        get_weight='temperature',  # The weight is based on temperature
        aggregation=pdk.types.String("sum"),
        radius_pixels=50,  # Adjust the radius for heatmap visualization
        intensity=1,  # Adjust intensity based on data
    )

# Continuously fetch data and update map
response = requests.get(url, stream=True)

# Initial heatmap layer
heatmap_layer = get_heatmap_layer(map_data)

# Deck to display the heatmap
deck = pdk.Deck(
    initial_view_state=initial_view,
    layers=[heatmap_layer],
    map_style='mapbox://styles/mapbox/dark-v10',
    tooltip={"text": "{temperature}°F at [{lat}, {lon}]"},
)

# Display the initial empty heatmap
map_chart = st.pydeck_chart(deck)

# Continuously fetch and update data
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

                    # Replace old data with new data in map_data
                    map_data = new_data

                    # Update the heatmap layer with the new data
                    heatmap_layer.data = map_data

                    # Recreate the deck to reflect the updated data
                    deck.layers = [heatmap_layer]

                    # Update the map in real-time
                    map_chart.pydeck_chart(deck)
                else:
                    st.error("Data format is incorrect.")
        except json.JSONDecodeError:
            st.error("Failed to decode JSON. Skipping this data point.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    # Optional: Add a small delay to control update rate
    time.sleep(1)
