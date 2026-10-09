# map.py — Create an interactive Folium map showing emissions by grid cell
# This script reads output/emissions.json and creates a map with CircleMarkers
# colored by emission intensity, with separate layers for Baseline and EV Scenario.

# --- Step 1: Import required libraries ---
import json  # For reading the emissions JSON file
import os  # For file path operations
import folium  # For creating interactive maps
from folium import LayerControl  # For adding layer toggle control

# --- Step 2: Define file paths ---
EMISSIONS_FILE = os.path.join("output", "emissions.json")  # Input: emissions data
OUTPUT_MAP = os.path.join("output", "emissions_map.html")  # Output: HTML map

# --- Step 3: Define map center (Cork, Ireland) ---
CENTER_LAT = 51.8985  # Latitude of Cork city center
CENTER_LON = -8.4756  # Longitude of Cork city center

# --- Step 4: Define grid cell parameters ---
GRID_SIZE = 3  # 3x3 grid = 9 cells
GRID_SPACING_KM = 0.5  # Each cell is ~500m apart

# --- Step 5: Define color gradient thresholds ---
# These values determine the color of each CircleMarker
LOW_THRESHOLD = 100  # Emissions below this are green
HIGH_THRESHOLD = 500  # Emissions above this are red

# --- Step 6: Read emissions data from JSON file ---
with open(EMISSIONS_FILE, "r") as f:  # Open emissions file for reading
    emissions_data = json.load(f)  # Load JSON data into a Python dictionary

# --- Step 7: Create the base map ---
m = folium.Map(
    location=[CENTER_LAT, CENTER_LON],  # Center on Cork
    zoom_start=14,  # Zoom level (14 = city level)
    tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",  # OSM tiles (no API key needed)
    attr="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors",  # Required attribution
)

# --- Step 8: Generate grid cell coordinates ---
# Create a 3x3 grid of points around the center
grid_cells = []  # List to store grid cell coordinates
lat_offset = -GRID_SPACING_KM  # Start with negative offset (south/west)
for i in range(GRID_SIZE):  # Loop over rows
    lon_offset = -GRID_SPACING_KM  # Reset longitude offset for each row
    for j in range(GRID_SIZE):  # Loop over columns
        # Calculate cell center coordinates
        cell_lat = CENTER_LAT + (lat_offset * 0.009)  # Convert km to degrees latitude
        cell_lon = CENTER_LON + (lon_offset * 0.014)  # Convert km to degrees longitude (adjusted for latitude)
        grid_cells.append((cell_lat, cell_lon))  # Add to grid cells list
        lon_offset += GRID_SPACING_KM  # Move east
    lat_offset += GRID_SPACING_KM  # Move north

# --- Step 9: Distribute emissions across grid cells ---
# For simplicity, we distribute total emissions evenly across all cells
# In a real project, this would be based on actual camera locations
num_cells = len(grid_cells)  # Total number of grid cells

# Calculate per-cell emissions for baseline
baseline_per_cell = emissions_data["baseline"]["total"] / num_cells  # Divide total by number of cells
# Calculate per-cell emissions for EV scenario
ev_per_cell = emissions_data["ev_scenario"]["total"] / num_cells  # Divide total by number of cells

# --- Step 10: Determine color based on emission value ---
def get_color(emission_value):
    """Return color based on emission intensity."""
    if emission_value < LOW_THRESHOLD:  # Low emissions
        return "#00ff00"  # Green
    elif emission_value < HIGH_THRESHOLD:  # Medium emissions
        return "#ffff00"  # Yellow
    else:  # High emissions
        return "#ff0000"  # Red

# --- Step 11: Create feature groups for layer control ---
# Baseline layer
baseline_layer = folium.FeatureGroup(name="Baseline")  # Create feature group for baseline
# EV Scenario layer
ev_layer = folium.FeatureGroup(name="EV Scenario")  # Create feature group for EV scenario

# --- Step 12: Add CircleMarkers for each grid cell ---
for idx, (cell_lat, cell_lon) in enumerate(grid_cells):  # Loop through each grid cell
    # Get emission values for this cell
    cell_baseline = baseline_per_cell  # Baseline emissions for this cell
    cell_ev = ev_per_cell  # EV scenario emissions for this cell

    # Get colors based on emission values
    baseline_color = get_color(cell_baseline)  # Color for baseline
    ev_color = get_color(cell_ev)  # Color for EV scenario

    # Create popup text for baseline
    baseline_popup = f"""
    <b>Grid Cell {idx + 1}</b><br>
    <b>Baseline Emissions:</b><br>
    Car: {emissions_data['baseline']['car'] / num_cells:.2f} g<br>
    Bus: {emissions_data['baseline']['bus'] / num_cells:.2f} g<br>
    Truck: {emissions_data['baseline']['truck'] / num_cells:.2f} g<br>
    Motorcycle: {emissions_data['baseline']['motorcycle'] / num_cells:.2f} g<br>
    <b>Total: {cell_baseline:.2f} g CO2</b>
    """

    # Create popup text for EV scenario
    ev_popup = f"""
    <b>Grid Cell {idx + 1}</b><br>
    <b>EV Scenario Emissions:</b><br>
    Car: {emissions_data['ev_scenario']['car'] / num_cells:.2f} g<br>
    Bus: {emissions_data['ev_scenario']['bus'] / num_cells:.2f} g<br>
    Truck: {emissions_data['ev_scenario']['truck'] / num_cells:.2f} g<br>
    Motorcycle: {emissions_data['ev_scenario']['motorcycle'] / num_cells:.2f} g<br>
    <b>Total: {cell_ev:.2f} g CO2</b>
    """

    # Add CircleMarker to baseline layer
    folium.CircleMarker(
        location=[cell_lat, cell_lon],  # Marker position
        radius=15,  # Radius in pixels
        color=baseline_color,  # Border color
        fill=True,  # Fill the circle
        fill_color=baseline_color,  # Fill color
        fill_opacity=0.6,  # Fill opacity
        popup=folium.Popup(baseline_popup, max_width=300),  # Popup on click
        tooltip=f"Cell {idx + 1}: {cell_baseline:.2f} g",  # Hover tooltip
    ).add_to(baseline_layer)  # Add to baseline layer

    # Add CircleMarker to EV scenario layer
    folium.CircleMarker(
        location=[cell_lat, cell_lon],  # Marker position
        radius=15,  # Radius in pixels
        color=ev_color,  # Border color
        fill=True,  # Fill the circle
        fill_color=ev_color,  # Fill color
        fill_opacity=0.6,  # Fill opacity
        popup=folium.Popup(ev_popup, max_width=300),  # Popup on click
        tooltip=f"Cell {idx + 1}: {cell_ev:.2f} g",  # Hover tooltip
    ).add_to(ev_layer)  # Add to EV scenario layer

# --- Step 13: Add layers to map ---
baseline_layer.add_to(m)  # Add baseline layer to map
ev_layer.add_to(m)  # Add EV scenario layer to map

# --- Step 14: Add layer control ---
LayerControl().add_to(m)  # Add layer toggle control to map

# --- Step 15: Add legend to map ---
legend_html = """
<div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
     background-color: white; padding: 10px; border-radius: 5px;
     font-size: 12px; border: 2px solid grey;">
     <b>Emissions Legend</b><br>
     <i style="background: #00ff00; width: 12px; height: 12px; display: inline-block;"></i> Low (&lt; 100 g)<br>
     <i style="background: #ffff00; width: 12px; height: 12px; display: inline-block;"></i> Medium (100-500 g)<br>
     <i style="background: #ff0000; width: 12px; height: 12px; display: inline-block;"></i> High (&gt; 500 g)
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))  # Add legend to map

# --- Step 16: Add title to map ---
title_html = """
<div style="position: fixed; top: 10px; left: 50px; z-index: 1000;
     background-color: white; padding: 10px; border-radius: 5px;
     font-size: 16px; font-weight: bold; border: 2px solid grey;">
     Vehicle Emissions Map — Cork, Ireland
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))  # Add title to map

# --- Step 17: Save the map to an HTML file ---
m.save(OUTPUT_MAP)  # Save map as interactive HTML

# --- Step 18: Print confirmation ---
print(f"Map saved to: {OUTPUT_MAP}")  # Print output file path
print(f"Open this file in a web browser to view the interactive map.")  # Print instructions
print(f"Map shows {num_cells} grid cells with Baseline and EV Scenario layers.")  # Print summary
