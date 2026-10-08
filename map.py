# map.py — Create an interactive Folium map showing emissions by location
# This script reads output/emissions.json and creates a heatmap
# showing where emissions are highest.

# --- Step 1: Import required libraries ---
import json  # For reading the emissions JSON file
import os  # For file path operations
import folium  # For creating interactive maps
from folium.plugins import HeatMap  # For adding heatmap layer

# --- Step 2: Define file paths ---
EMISSIONS_FILE = os.path.join("output", "emissions.json")  # Input: emissions data
OUTPUT_MAP = os.path.join("output", "emissions_map.html")  # Output: HTML map

# --- Step 3: Define placeholder GPS coordinates for each video ---
# In a real project, these would come from your video metadata or manual input
# For this prototype, we assign approximate coordinates to each video
VIDEO_LOCATIONS = {
    "18211405-uhd_3840_2160_24fps.mp4": {"lat": 51.5074, "lon": -0.1278, "name": "London A"},
    "18437773-uhd_3840_2160_50fps.mp4": {"lat": 48.8566, "lon": 2.3522, "name": "Paris A"},
    "20770166-hd_1080_1920_30fps.mp4": {"lat": 40.7128, "lon": -74.0060, "name": "New York A"},
    "coverr-cars-driving-on-busy-street-9014-1080p.mp4": {"lat": 35.6762, "lon": 139.6503, "name": "Tokyo A"},
    "coverr-two-way-road-8177-1080p.mp4": {"lat": 52.5200, "lon": 13.4050, "name": "Berlin A"},
    "coverr-yellow-taxi-7335-1080p.mp4": {"lat": 40.7128, "lon": -74.0060, "name": "New York B"},
    "traffic.mp4": {"lat": 51.5074, "lon": -0.1278, "name": "London B"},
}

# --- Step 4: Read emissions data from JSON file ---
with open(EMISSIONS_FILE, "r") as f:  # Open emissions file for reading
    emissions_data = json.load(f)  # Load JSON data into a Python dictionary

# --- Step 5: Prepare data for the heatmap ---
heat_data = []  # List of [lat, lon, intensity] for HeatMap
location_markers = []  # List of (lat, lon, popup_text) for markers

# --- Step 6: Loop through each video's emissions ---
for video_name, emissions in emissions_data.items():  # Iterate over each video
    # Get location for this video (default to London if not found)
    location = VIDEO_LOCATIONS.get(video_name, {"lat": 51.5074, "lon": -0.1278, "name": "Unknown"})

    # Get total CO2 emissions for this video
    total_co2 = emissions.get("total", {}).get("co2_g", 0)  # Get CO2 total, default 0

    # Add to heat data: [lat, lon, intensity]
    # Intensity is normalized CO2 (divided by 1000 for better visualization)
    heat_data.append([location["lat"], location["lon"], total_co2 / 1000.0])

    # Create popup text for the marker
    popup_text = f"""
    <b>{location['name']}</b><br>
    Video: {video_name}<br>
    CO2: {total_co2:,.0f} g<br>
    NOx: {emissions.get('total', {}).get('nox_g', 0):.2f} g
    """

    # Add to markers list
    location_markers.append((location["lat"], location["lon"], popup_text))

# --- Step 7: Create the base map ---
# Center on the first location, zoom level 5 (world view)
m = folium.Map(
    location=[51.5074, -0.1278],  # Center coordinates (London)
    zoom_start=5,  # Initial zoom level (1=world, 18=street)
    tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",  # Direct OSM tile URL (no API key needed)
    attr="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors",  # Required attribution
)

# --- Step 8: Add heatmap layer ---
HeatMap(
    heat_data,  # Data points [lat, lon, intensity]
    min_opacity=0.3,  # Minimum opacity for low-intensity areas
    radius=25,  # Radius of each heat point in pixels
    blur=15,  # Blur factor for smooth gradients
    max_zoom=10,  # Maximum zoom for heat points
).add_to(m)  # Add heatmap to the map

# --- Step 9: Add markers for each location ---
for lat, lon, popup_text in location_markers:  # Loop through each location
    folium.Marker(
        location=[lat, lon],  # Marker position
        popup=folium.Popup(popup_text, max_width=300),  # Popup on click
        tooltip="Click for details",  # Hover tooltip
    ).add_to(m)  # Add marker to the map

# --- Step 10: Add a legend/title to the map ---
title_html = """
<div style="position: fixed; top: 10px; left: 50px; z-index: 1000;
     background-color: white; padding: 10px; border-radius: 5px;
     font-size: 14px; font-weight: bold;">
     Vehicle Emissions Heatmap
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))  # Add title to map

# --- Step 11: Save the map to an HTML file ---
m.save(OUTPUT_MAP)  # Save map as interactive HTML

# --- Step 12: Print confirmation ---
print(f"Map saved to: {OUTPUT_MAP}")
print(f"Open this file in a web browser to view the interactive map.")
print(f"Heatmap shows {len(heat_data)} locations.")
