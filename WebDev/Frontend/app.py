
import streamlit as st
import requests
import pandas as pd
import json
import pydeck as pdk
import time

# Set page config
st.set_page_config(page_title="Real-time Environmental Monitoring", layout="wide")

# Custom CSS for pastel colors and prettier design
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

# Define thresholds for each parameter
TEMP_CRITICAL, TEMP_WARNING = 80, 60
UV_CRITICAL, UV_WARNING = 8, 5
HUMIDITY_CRITICAL, HUMIDITY_WARNING = 90, 70
PRESSURE_CRITICAL, PRESSURE_WARNING = 1020, 1000
AIR_QUALITY_CRITICAL, AIR_QUALITY_WARNING = 150, 100

# Define functions for colors based on temperature
def get_temperature_color(temp):
    if temp < 50:
        return [173, 216, 230]  # Light Blue for cool
    elif temp < 60:
        return [144, 238, 144]  # Light Green for moderate
    return [255, 182, 193]      # Light Pink for hot

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
view_option = st.radio("Select map view", ("Scatter View", "Heatmap View", "Choropleth View"))
# Map initialization
initial_view = pdk.ViewState(latitude=11.0, longitude=78.0, zoom=6)

# Create empty map chart
scatterplot_layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_data,
    get_position='[lon, lat]',
    get_fill_color='color',
    get_radius=3000,
    pickable=True,
)
heatmap_layer = pdk.Layer(
    'HeatmapLayer',
    data=map_data,
    get_position=['lon', 'lat'],
    get_weight='value',
    radius_pixels=20,
)
choropleth_layer = pdk.Layer(
    'GeoJsonLayer',
    data=map_data,
    get_fill_color=[255, 0, 0, 100],
    get_line_color=[0, 0, 0],
    line_width_min_pixels=1,
    pickable=True,
)
deck = pdk.Deck(
    initial_view_state=initial_view,
    layers=[scatterplot_layer],
    map_style='mapbox://styles/mapbox/dark-v10',
    tooltip={"text": "Temp: {temperature}°F, UV: {uv}, Humidity: {humidity}%, Air Quality: {airQuality}"}
)

map_chart = st.pydeck_chart(deck)

# Function to classify points based on threshold values
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
                        
                        # Update real-time metrics on cards (display averages)
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
                        
                        # Update scatterplot layer
                        if view_option=="Scatter View":
                            layer=scatterplot_layer
                        if view_option=="Heatmap View":
                            layer=heatmap_layer
                        if view_option=="Choropleth View":
                            layer=choropleth_layer
                        layer.data = map_data
                        deck = pdk.Deck(
                            initial_view_state=initial_view,
                            layers=[layer],
                            map_style='mapbox://styles/mapbox/dark-v10',
                            tooltip={"text": "{temperature}°F at [{lat}, {lon}]"},
                        )
                        map_chart.pydeck_chart(deck)
                    else:
                        st.error("Data format is incorrect.")
            except json.JSONDecodeError:
                st.error("Failed to decode JSON.")
            except Exception as e:
                st.error(f"Error: {e}")
        
        time.sleep(1)  # Optional delay for smoother updates
except requests.exceptions.RequestException as e:
    st.error(f"Failed to connect to the server: {e}")
