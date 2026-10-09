# app.py — Streamlit dashboard for the Vehicle Emissions project
# This script creates an interactive web dashboard showing:
# - Vehicle counts per video
# - Estimated emissions (Baseline vs EV Scenario)
# - Interactive map of emissions by location

# --- Step 1: Import required libraries ---
import streamlit as st  # For creating the web dashboard
import json  # For reading JSON data files
import os  # For file path operations
import pandas as pd  # For creating data tables

# --- Step 2: Configure the Streamlit page ---
st.set_page_config(
    page_title="Vehicle Emissions Dashboard",  # Browser tab title
    page_icon="car",  # Browser tab icon
    layout="wide",  # Use full page width
)

# --- Step 3: Define file paths ---
COUNTS_FILE = os.path.join("output", "all_counts.json")  # Vehicle counts
EMISSIONS_FILE = os.path.join("output", "emissions.json")  # Emissions data
MAP_FILE = os.path.join("output", "emissions_map.html")  # Folium map HTML

# --- Step 4: Load data from JSON files ---
@st.cache_data  # Cache the data so it doesn't reload on every interaction
def load_data():
    """Load counts and emissions data from JSON files."""
    # Load vehicle counts
    with open(COUNTS_FILE, "r") as f:  # Open counts file
        counts = json.load(f)  # Load counts data

    # Load emissions data
    with open(EMISSIONS_FILE, "r") as f:  # Open emissions file
        emissions = json.load(f)  # Load emissions data

    return counts, emissions  # Return both datasets

# --- Step 5: Load the data ---
counts, emissions = load_data()  # Call the load function

# --- Step 6: Create the dashboard title ---
st.title("Vision-Based Vehicle Detection for Street-Level Emissions")
st.markdown("---")  # Horizontal line separator

# --- Step 7: Create two columns for layout ---
col1, col2 = st.columns(2)  # Split page into 2 equal columns

# --- Step 8: Left column — Vehicle Counts ---
with col1:  # Work inside the left column
    st.subheader("Vehicle Counts")  # Section title

    # Create a list to hold table data
    table_data = []  # Empty list for table rows

    # Loop through each video
    for video_name, vehicle_counts in counts.items():  # Iterate over videos
        # Create a row for this video
        row = {
            "Video": video_name,  # Video filename
            "Cars": vehicle_counts.get("car", 0),  # Car count
            "Motorcycles": vehicle_counts.get("motorcycle", 0),  # Motorcycle count
            "Buses": vehicle_counts.get("bus", 0),  # Bus count
            "Trucks": vehicle_counts.get("truck", 0),  # Truck count
            "Total": sum(vehicle_counts.values()),  # Sum of all vehicles
        }
        table_data.append(row)  # Add row to table data

    # Convert to DataFrame for nice display
    df_counts = pd.DataFrame(table_data)  # Create pandas DataFrame

    # Display the table
    st.dataframe(df_counts, use_container_width=True)  # Show table in Streamlit

# --- Step 9: Right column — Emissions ---
with col2:  # Work inside the right column
    st.subheader("Estimated Emissions (CO2)")  # Section title

    # Get baseline and ev_scenario data
    baseline = emissions.get("baseline", {})  # Baseline emissions
    ev_scenario = emissions.get("ev_scenario", {})  # EV scenario emissions

    # Create emissions comparison table
    emissions_table = []  # Empty list for emissions rows

    # Define vehicle types to display
    vehicle_types = ["car", "bus", "truck", "motorcycle"]  # All vehicle types

    # Loop through each vehicle type
    for vt in vehicle_types:  # For each vehicle type
        # Get baseline and EV values for this vehicle type
        baseline_val = baseline.get(vt, 0)  # Baseline emissions
        ev_val = ev_scenario.get(vt, 0)  # EV scenario emissions

        # Create a row
        row = {
            "Vehicle Type": vt.capitalize(),  # Vehicle type name
            "Baseline (g)": round(baseline_val, 2),  # Baseline emissions
            "EV Scenario (g)": round(ev_val, 2),  # EV scenario emissions
            "Reduction (g)": round(baseline_val - ev_val, 2),  # Reduction amount
        }
        emissions_table.append(row)  # Add row

    # Add total row
    emissions_table.append({
        "Vehicle Type": "TOTAL",  # Total label
        "Baseline (g)": round(baseline.get("total", 0), 2),  # Total baseline
        "EV Scenario (g)": round(ev_scenario.get("total", 0), 2),  # Total EV
        "Reduction (g)": round(baseline.get("total", 0) - ev_scenario.get("total", 0), 2),  # Total reduction
    })

    # Convert to DataFrame
    df_emissions = pd.DataFrame(emissions_table)  # Create pandas DataFrame

    # Display the table
    st.dataframe(df_emissions, use_container_width=True)  # Show table

# --- Step 10: Summary statistics ---
st.markdown("---")  # Separator
st.subheader("Summary Statistics")  # Section title

# Calculate totals across all videos
total_vehicles = sum(sum(v.values()) for v in counts.values())  # All vehicles
total_baseline = emissions.get("baseline", {}).get("total", 0)  # Total baseline CO2
total_ev = emissions.get("ev_scenario", {}).get("total", 0)  # Total EV CO2
reduction_pct = emissions.get("reduction_percent", 0)  # Percent reduction

# Create three metric columns
m1, m2, m3, m4 = st.columns(4)  # Four equal columns for metrics

with m1:  # First metric
    st.metric("Total Vehicles", f"{total_vehicles}")  # Show total vehicles

with m2:  # Second metric
    st.metric("Baseline CO2", f"{total_baseline/1000:.2f} kg")  # Show total baseline CO2

with m3:  # Third metric
    st.metric("EV Scenario CO2", f"{total_ev/1000:.2f} kg")  # Show total EV CO2

with m4:  # Fourth metric
    st.metric("Reduction", f"{reduction_pct:.1f}%")  # Show percent reduction

# --- Step 11: Map section ---
st.markdown("---")  # Separator
st.subheader("Emissions Map")  # Section title

# Check if map file exists
if os.path.exists(MAP_FILE):  # If map HTML file exists
    # Read the HTML content
    with open(MAP_FILE, "r", encoding="utf-8") as f:  # Open map file
        map_html = f.read()  # Read HTML content

    # Display the map using iframe
    st.components.v1.html(map_html, height=500)  # Embed map in Streamlit
else:
    st.warning("Map file not found. Run map.py first to generate the map.")  # Warning message

# --- Step 12: Footer ---
st.markdown("---")  # Separator
st.caption("Vision-Based Vehicle Detection for Street-Level Emissions Mapping — PhD Portfolio Project")  # Footer text
