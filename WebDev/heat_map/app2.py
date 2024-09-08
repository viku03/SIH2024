import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

# Step 1: Generate random temperature data
# Replace this with your real data
num_points = 50  # Number of random points
lats = np.random.uniform(low=8.1, high=13.8, size=num_points)  # Latitude range for Tamil Nadu
lons = np.random.uniform(low=76.9, high=80.3, size=num_points)  # Longitude range for Tamil Nadu
temps = np.random.uniform(low=40, high=70, size=num_points)  # Temperature range in °F

# Step 2: Create grid data
grid_x, grid_y = np.mgrid[min(lons):max(lons):100j, min(lats):max(lats):100j]
grid_z = griddata((lons, lats), temps, (grid_x, grid_y), method='cubic')

# Step 3: Plot the heatmap with contour lines
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

# Show plot
plt.show()
