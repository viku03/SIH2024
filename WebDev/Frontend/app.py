
import requests
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import json
import time
API_KEY = 'aca430e0c725352d8b8c78555a0c7f62'  # Replace with your OpenWeatherMap API key
CITY = 'Chennai'
BASE_URL = 'http://api.openweathermap.org/data/2.5/'

url = "http://127.0.0.1:5000/data" 
def fetch_weather_data():
    weather_url = f"{BASE_URL}weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(weather_url)
    data = response.json()
    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "weather_description": data["weather"][0]["description"]
    }

def fetch_uv_index():
    latitude, longitude = 13.0827, 80.2707
    uv_url = f"{BASE_URL}uvi?lat={latitude}&lon={longitude}&appid={API_KEY}"
    response = requests.get(uv_url)
    data = response.json()
    return data["value"]

st.set_page_config(page_title="Chennai Environmental Monitoring", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    .metric-box {
        border-radius: 5px;
        padding: 10px;
        margin: 30px;
        text-align: center;
        font-size: 25px;
        color: white;
        width: 600px;
        opacity: 0.8;
        word-spacing: 4px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        font-family: 'Roboto', sans-serif;
    }
    .uv_intensity { background-color: #FFC300; }
    .temperature { background-color: #FF5733; }
    .humidity { background-color: #33C1FF; }
    .pressure { background-color: #003366; }
    .air_quality { background-color: #900C3F; }
    </style>
    """, unsafe_allow_html=True
)

st.sidebar.header("Menu")
menu = st.sidebar.radio("Navigate", ['Home', 'Status Monitoring Points', 'Warning List'])

st.sidebar.header("Filters")
st.sidebar.selectbox("Select Zone", ["All zones", "Zone 1", "Zone 2"])
st.sidebar.text_input("Monitoring Point Search")

weather_data = fetch_weather_data()
uv_index = fetch_uv_index()

map_data = pd.DataFrame(columns=['lat', 'lon', 'temperature', 'color'])

# Define color scale based on temperature
def get_color(temperature):
    if temperature < 50:
        return [0, 0, 255]  # Blue for cooler temperatures
    elif temperature < 60:
        return [0, 255, 0]  # Green for moderate temperatures
    else:
        return [255, 0, 0]  # Red for warmer temperatures

if menu == "Home":
    st.title("Environmental Monitoring - Chennai")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Heat Wave", "In Progress", "Max 23.8°C", delta_color="inverse")
    col2.metric("CO2 Level", "Acceptable", "473 ppm")
    col3.metric("PM 2.5 Legal Limits", "Exceeds", "29 µg/m³")
    col4.metric("PM 10 Legal Limits", "Ok", "32 µg/m³")

    st.header("Current Alerts and Conditions")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="metric-box uv_intensity">
             UV Intensity <b> {uv_index:.1f} </b> High
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-box temperature">
            Temperature <b> {weather_data["temperature"]:.1f}°C </b> {weather_data["weather_description"].capitalize()}
            </div>
            """, unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-box humidity">
             Humidity <b> {weather_data["humidity"]}% </b> Low Decrement
            </div>
            """, unsafe_allow_html=True
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="metric-box pressure">
             Barometric Pressure <b> {weather_data["pressure"]} hPa </b> Stable
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="metric-box air_quality">
            Air Quality  <b> 28 µg/m³</b> Low Increment
            </div>
            """, unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            """
            <div class="metric-box air_quality">
            Extra Metric  <b> Value </b> Placeholder
            </div>
            """, unsafe_allow_html=True
        )

    st.header("Map Selection")

    map_option = st.radio("Select Map", ["Monitoring Points Map", "Thermal Map"])

    if map_option == "Monitoring Points Map":
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
        '''elif map_option == "Thermal Map":
            st.header("Thermal Map")

            thermal_data = pd.DataFrame(
                np.random.randn(100, 2) / [50, 50] + [13.0827, 80.2707],
                columns=['lat', 'lon']
            )
            thermal_data['temperature'] = np.random.uniform(25, 40, size=thermal_data.shape[0])

            color_range = [
                [0, 0, 255, 255],  # Blue
                [255, 0, 0, 255]   # Red
            ]

            layer_thermal = pdk.Layer(
                'HeatmapLayer',
                data=thermal_data,
                get_position='[lon, lat]',
                get_weight='temperature',
                radius_pixels=50,
                intensity=1,
                color_range=color_range
            )

            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/dark-v10',
                initial_view_state=pdk.ViewState(
                    latitude=13.0827,
                    longitude=80.2707,
                    zoom=12,
                    pitch=50,
                ),
                layers=[layer_thermal],
            ))'''
