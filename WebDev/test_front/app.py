import streamlit as st
import requests
import pandas as pd
import json
import pydeck as pdk
import time

# Set page config
st.set_page_config(page_title="Real-time Environmental Monitoring", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-label {
        font-size: 14px;
        color: #718096;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #4a5568;
    }
    .status-card {
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }
    .status-critical {
        background-color: #fed7d7;
        color: #9b2c2c;
    }
    .status-warning {
        background-color: #feebc8;
        color: #9c4221;
    }
    .status-ok {
        background-color: #c6f6d5;
        color: #2f855a;
    }
</style>
""", unsafe_allow_html=True)

# Define thresholds for parameters
TEMP_CRITICAL, TEMP_WARNING = 1000, 1000
UV_CRITICAL, UV_WARNING = 600, 400
HUMIDITY_CRITICAL, HUMIDITY_WARNING = 9000, 7000
PRESSURE_CRITICAL, PRESSURE_WARNING = 120000, 110000
AIR_QUALITY_CRITICAL, AIR_QUALITY_WARNING = 2000, 1500

# Function to assign colors based on temperature
def get_temperature_color(temp):
    if temp < 50:
        return [173, 216, 230]  # Light Blue for cool
    elif temp < 60:
        return [144, 238, 144]  # Light Green for moderate
    return [255, 182, 193]  # Light Pink for hot

# Flask server URL
url = "http://127.0.0.1:5000/data"  # Example Flask URL

# DataFrame to store monitoring point data
map_data = pd.DataFrame(columns=['lat', 'lon', 'temperature', 'uv', 'humidity', 'pressure', 'airQuality', 'color'])

# Main Dashboard Layout
st.title("Real-time Environmental Monitoring Dashboard")

# Real-time data cards
st.markdown("### Real-time Environmental Data (Averages)")
col_temp, col_uv, col_hum, col_press, col_air = st.columns(5)

# Initialize placeholder metrics
temp_metric = col_temp.empty()
uv_metric = col_uv.empty()
hum_metric = col_hum.empty()
press_metric = col_press.empty()
air_metric = col_air.empty()

# View selection for map visualization
view_option = st.radio("Select map view", ("Scatter View", "Heatmap View"))

# Map initialization
initial_view = pdk.ViewState(latitude=12.843125306462428, longitude=80.1545516362617, zoom=16)
# Scatterplot layer
scatterplot_layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_data,
    get_position='[lon, lat]',
    get_fill_color='color',
    get_radius=10,
    pickable=True,
)

# Heatmap layer
heatmap_layer = pdk.Layer(
    'HeatmapLayer',
    data=map_data,
    get_position=['lon', 'lat'],
    get_weight='temperature',  # Assuming temperature is the heatmap metric
    radius_pixels=50,
    intensity=1,
    threshold=0.1,
    opacity = 0.4
)

# Choropleth layer
with open("../JSON/TamilNadu.geojson") as f:
    geojson_data = json.load(f)

choropleth_layer = pdk.Layer(
    "GeoJsonLayer",
    geojson_data,
    stroked=False,
    filled=True,
    get_fill_color=[0, 128, 255, 180],  # Blueish color for Tamil Nadu
    get_line_color=[255, 255, 255],
    line_width_min_pixels=1,
)

# Create map chart (default to Scatterplot)
deck = pdk.Deck(
    initial_view_state=initial_view,
    layers=[scatterplot_layer],
    map_style='mapbox://styles/mapbox/light-v9',
    tooltip={"text": "Temp: {temperature}°F, UV: {uv}, Humidity: {humidity}%, Air Quality: {airQuality}"}
)
deck_heatmap = pdk.Deck(
    initial_view_state=initial_view,
    layers=[heatmap_layer],
    map_style='mapbox://styles/mapbox/light-v9',
    tooltip={"text": "Temp: {temperature}°F, UV: {uv}, Humidity: {humidity}%, Air Quality: {airQuality}"}
)
deck_choro =  pdk.Deck(
    initial_view_state=initial_view,
    layers=[choropleth_layer],
    map_style='mapbox://styles/mapbox/light-v9',
    tooltip={"text": "Temp: {temperature}°F, UV: {uv}, Humidity: {humidity}%, Air Quality: {airQuality}"}
)
map_chart = st.pydeck_chart(deck)

# Function to classify points based on thresholds
def classify_points(data):
    critical_count = sum((data['temperature'] >= TEMP_CRITICAL) | (data['uv'] >= UV_CRITICAL) | 
                         (data['humidity'] >= HUMIDITY_CRITICAL) | (data['pressure'] >= PRESSURE_CRITICAL) | 
                         (data['airQuality'] >= AIR_QUALITY_CRITICAL))
    warning_count = sum((data['temperature'] >= TEMP_WARNING) | (data['uv'] >= UV_WARNING) | 
                        (data['humidity'] >= HUMIDITY_WARNING) | (data['pressure'] >= PRESSURE_WARNING) | 
                        (data['airQuality'] >= AIR_QUALITY_WARNING)) - critical_count
    ok_count = len(data) - critical_count - warning_count
    return critical_count, warning_count, ok_count

# Status section
st.markdown("### Status of Monitoring Points")
col1, col2, col3 = st.columns(3)
critical_metric = col1.empty()
warning_metric = col2.empty()
ok_metric = col3.empty()

# Continuously fetch and update data
try:
    response = requests.get(url, stream=True)
    for line in response.iter_lines():
        if line:
            try:
                decoded_line = line.decode('utf-8').strip()
                if decoded_line.startswith("data:"):
                    json_data = decoded_line[5:]
                    data = json.loads(json_data)
                    
                    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                        # Process new data
                        new_data = pd.DataFrame(data)
                        new_data['color'] = new_data['temperature'].apply(get_temperature_color)
                        
                        # Replace old map data
                        map_data = new_data
                        
                        # Compute average values for each metric
                        avg_temp = new_data['temperature'].mean()
                        avg_uv = new_data['uv'].mean()
                        avg_humidity = new_data['humidity'].mean()
                        avg_pressure = new_data['pressure'].mean()
                        avg_air_quality = new_data['airQuality'].mean()
                        
                        # Update real-time metrics on cards
                        temp_metric.metric("Avg Temperature", f"{avg_temp:.2f}°F")
                        uv_metric.metric("Avg UV Index", f"{avg_uv:.2f}")
                        hum_metric.metric("Avg Humidity", f"{avg_humidity:.2f}%")
                        press_metric.metric("Avg Pressure", f"{avg_pressure:.2f} hPa")
                        air_metric.metric("Avg Air Quality", f"{avg_air_quality:.2f}")
                        
                        # Classify points based on the thresholds
                        critical_count, warning_count, ok_count = classify_points(new_data)
                        
                        # Update status metrics
                        total_points = len(new_data)
                        critical_metric.markdown(f'<div class="status-card status-critical"><div class="metric-label">Critical</div><div class="metric-value">{critical_count}/{total_points}</div></div>', unsafe_allow_html=True)
                        warning_metric.markdown(f'<div class="status-card status-warning"><div class="metric-label">Warning</div><div class="metric-value">{warning_count}/{total_points}</div></div>', unsafe_allow_html=True)
                        ok_metric.markdown(f'<div class="status-card status-ok"><div class="metric-label">OK</div><div class="metric-value">{ok_count}/{total_points}</div></div>', unsafe_allow_html=True)
                        
                        # Update the map layer based on view option
                        if view_option == "Scatter View":
                            layer = scatterplot_layer
                        elif view_option == "Heatmap View":
                            layer = heatmap_layer
                        elif view_option == "Choropleth View":
                            layer = choropleth_layer
                        
                        # Render the updated map
                        if view_option == "Scatter View" or view_option=="Heatmap View":
                            layer.data = map_data
                            deck = pdk.Deck(
                                initial_view_state=initial_view,
                                layers=[layer],
                                map_style='mapbox://styles/mapbox/light-v9' if view_option != "Scatter View" else 'mapbox://styles/mapbox/dark-v11',
                                tooltip={"text": "Temp:{temperature}°F\nUV Index:{uv}\nHumidity:{humidity}%\nAir Pressure:{pressure}hPa\nAir Quality:{airQuality}\n at [{lat}, {lon}]"},
                            )
                            map_chart.pydeck_chart(deck)
                        else:
                            layer.data = map_data
                            map_chart.pydeck_chart(pdk.Deck(
                                layers=[choropleth_layer],
                                initial_view_state=initial_view,
                                map_style='mapbox://styles/mapbox/light-v9',  # Choose a suitable Mapbox style
                                tooltip={"text": "Temp:{temperature}°F\nUV Index:{uv}\nHumidity:{humidity}%\nAir Pressure:{pressure}hPa\nAir Quality:{airQuality}\n at [{lat}, {lon}]"},
                            ))

                    else:
                        st.error("Data format is incorrect.")
            except json.JSONDecodeError:
                st.error("Failed to decode JSON.")
            except Exception as e:
                st.error(f"Error: {e}")
        
        time.sleep(1)  # Optional delay for smoother updates
except requests.exceptions.RequestException as e:
    st.error(f"Failed to connect to the server: {e}")
