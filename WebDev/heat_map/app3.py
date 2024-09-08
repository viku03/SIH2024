import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from scipy.interpolate import griddata
import requests
import pandas as pd
import json

# Step 1: Fetch the temperature data from the Flask server
sse_url = "http://127.0.0.1:5000/data"  # Change this to your Flask server URL

def get_temperature_data():
    response = requests.get(sse_url, stream=True)
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith('data:'):
                # Parse the JSON data from SSE
                data = json.loads(decoded_line[5:])
                return pd.DataFrame(data)  # Convert JSON to pandas DataFrame

# Step 2: Get the data from the Flask server
data = get_temperature_data()

# Check if data is fetched
if data is not None and not data.empty:
    # Extract latitude, longitude, and temperature from the data
    lats = data['lat'].values
    lons = data['lon'].values
    temps = data['temperature'].values

    # Step 3: Create grid data for contour plot
    grid_x, grid_y = np.mgrid[min(lons):max(lons):100j, min(lats):max(lats):100j]
    grid_z = griddata((lons, lats), temps, (grid_x, grid_y), method='cubic')

    # Step 4: Plot the heatmap with contour lines
    plt.figure(figsize=(8, 6))

    # Heatmap (with gradient)
    heatmap = plt.contourf(grid_x, grid_y, grid_z, levels=100, cmap='coolwarm')  # Adjust cmap as needed

    # Contour lines
    contours = plt.contour(grid_x, grid_y, grid_z, levels=10, colors='white')

    # Add labels to contour lines
    plt.clabel(contours, inline=True, fontsize=8, fmt='%1.1f °F')

    # Add color bar to represent temperature gradient
    plt.colorbar(heatmap, label='Temperature (°F)')

    # Labels and title
    plt.title("Temperature Heatmap with Contours")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    # Step 5: Display the plot in Streamlit
    st.pyplot(plt)

else:
    st.error("No data available from the server.")
