# app.py — Streamlit dashboard for the Vehicle Emissions project
# This script creates an interactive web dashboard with 4 tabs:
# - Annotated Video
# - Emission Counts
# - Emissions Map
# - Scenario Comparison

# --- Step 1: Import required libraries ---
import streamlit as st  # For creating the web dashboard
import json  # For reading JSON data files
import os  # For file path operations
import pandas as pd  # For creating data tables
import subprocess  # For running detect.py from within the app

# --- Step 2: Configure the Streamlit page ---
st.set_page_config(
    page_title="Vehicle Emissions Dashboard",  # Browser tab title
    page_icon="car",  # Browser tab icon
    layout="wide",  # Use full page width
)

# --- Step 3: Add sidebar with project info ---
with st.sidebar:  # Work inside the sidebar
    st.title("Vehicle Emissions Dashboard")  # Sidebar title
    st.markdown("---")  # Separator line
    st.markdown("### About")  # Section header
    st.markdown(
        "This dashboard visualizes vehicle detection results "
        "and estimated CO2 emissions from traffic videos. "
        "It compares baseline emissions with an EV adoption scenario."
    )  # Brief description
    st.markdown("---")  # Separator line
    st.markdown("### Pipeline")  # Section header
    st.markdown("1. Detect vehicles with YOLOv8")  # Step 1
    st.markdown("2. Track vehicles across frames")  # Step 2
    st.markdown("3. Calculate emissions")  # Step 3
    st.markdown("4. Visualize on map")  # Step 4
    st.markdown("---")  # Separator line
    st.markdown("Portfolio Project")  # Footer text

# --- Step 4: Define file paths ---
COUNTS_FILE = os.path.join("output", "all_counts.json")  # Vehicle counts
EMISSIONS_FILE = os.path.join("output", "emissions.json")  # Emissions data
MAP_FILE = os.path.join("output", "emissions_map.html")  # Folium map HTML
VIDEO_DIR = os.path.join("output", "annotated_videos")  # Directory with annotated videos

# --- Step 5: Load data from JSON files ---
@st.cache_data  # Cache the data so it doesn't reload on every interaction
def load_json(filepath):
    """Load JSON data from a file, return empty dict if missing."""
    if os.path.exists(filepath):  # Check if file exists
        with open(filepath, "r") as f:  # Open file for reading
            return json.load(f)  # Load and return JSON data
    return {}  # Return empty dict if file missing

# Load all data files
counts = load_json(COUNTS_FILE)  # Load vehicle counts
emissions = load_json(EMISSIONS_FILE)  # Load emissions data

# --- Step 6: Create dashboard title ---
st.title("Vision-Based Vehicle Detection for Street-Level Emissions")  # Main title
st.markdown("---")  # Horizontal line separator

# --- Step 7: Create 4 tabs ---
tab1, tab2, tab3, tab4 = st.tabs(
    ["Annotated Video", "Emission Counts", "Emissions Map", "Scenario Comparison"]
)  # Create 4 tabs with labels

# ==================== TAB 1: Annotated Video ====================
with tab1:  # Work inside the first tab
    st.subheader("Annotated Video")  # Tab section title
    st.markdown("This tab shows traffic videos with detected vehicles highlighted by bounding boxes, class labels, and tracking IDs.")  # Caption

    # Check if video directory exists and has videos
    video_files = []
    if os.path.exists(VIDEO_DIR):  # If annotated videos directory exists
        # Get list of video files
        video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith((".mp4", ".avi", ".mov"))]  # Filter video files

    if video_files:  # If video files found
        # Let user select a video
        selected_video = st.selectbox("Select a video:", video_files)  # Dropdown to select video
        video_path = os.path.join(VIDEO_DIR, selected_video)  # Full path to selected video
        st.video(video_path)  # Play the selected video
        st.caption(f"Showing: {selected_video}")  # Show selected video name
    else:
        # Show message and button to run detection
        st.info("No annotated videos found. Click the button below to run vehicle detection.")
        if st.button("Run Detection"):
            with st.spinner("Running detection... This may take a few minutes."):
                try:
                    # Run detect.py using the same Python executable
                    result = subprocess.run(
                        ["python", "detect.py"],
                        capture_output=True,
                        text=True,
                        timeout=600  # 10 minute timeout
                    )
                    if result.returncode == 0:
                        st.success("Detection complete! Refresh the page to see annotated videos.")
                    else:
                        st.error(f"Detection failed: {result.stderr}")
                except subprocess.TimeoutExpired:
                    st.error("Detection timed out. Please run detect.py manually.")
                except Exception as e:
                    st.error(f"Error running detection: {str(e)}")

# ==================== TAB 2: Emission Counts ====================
with tab2:  # Work inside the second tab
    st.subheader("Vehicle Counts")  # Tab section title
    st.markdown("This table shows the number of vehicles detected in each traffic video, broken down by vehicle type.")  # Caption

    # Check if counts data is available
    if counts:  # If counts data exists
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

        # Create bar chart showing totals by vehicle type
        st.subheader("Vehicle Type Distribution")  # Chart section title

        # Aggregate counts across all videos
        total_by_type = {"Car": 0, "Motorcycle": 0, "Bus": 0, "Truck": 0}  # Initialize totals
        for video_counts in counts.values():  # Loop through each video
            total_by_type["Car"] += video_counts.get("car", 0)  # Sum cars
            total_by_type["Motorcycle"] += video_counts.get("motorcycle", 0)  # Sum motorcycles
            total_by_type["Bus"] += video_counts.get("bus", 0)  # Sum buses
            total_by_type["Truck"] += video_counts.get("truck", 0)  # Sum trucks

        # Create bar chart
        st.bar_chart(total_by_type)  # Show bar chart
    else:
        st.warning("output/all_counts.json not found. Run detect.py first to generate counts.")  # Warning if file missing

# ==================== TAB 3: Emissions Map ====================
with tab3:  # Work inside the third tab
    st.subheader("Emissions Map")  # Tab section title
    st.markdown("This map shows estimated CO2 emissions across a grid of locations in Cork, Ireland. Use the layer control to toggle between Baseline and EV Scenario.")  # Caption

    # Check if map file exists
    if os.path.exists(MAP_FILE):  # If map HTML file exists
        # Read the HTML content
        with open(MAP_FILE, "r", encoding="utf-8") as f:  # Open map file
            map_html = f.read()  # Read HTML content

        # Display the map using iframe
        st.components.v1.html(map_html, height=600)  # Embed map in Streamlit
    else:
        st.warning("output/emissions_map.html not found. Run map.py first to generate the map.")  # Warning if file missing

# ==================== TAB 4: Scenario Comparison ====================
with tab4:  # Work inside the fourth tab
    st.subheader("Scenario Comparison")  # Tab section title
    st.markdown("This tab compares baseline emissions with an EV adoption scenario where 30% of cars are replaced with electric vehicles (0 g/km tailpipe emissions).")  # Caption

    # Check if emissions data is available
    if emissions:  # If emissions data exists
        # Get baseline and ev_scenario data
        baseline = emissions.get("baseline", {})  # Baseline emissions
        ev_scenario = emissions.get("ev_scenario", {})  # EV scenario emissions
        reduction_pct = emissions.get("reduction_percent", 0)  # Percent reduction

        # Display percent reduction prominently
        st.metric("Emissions Reduction", f"{reduction_pct:.1f}%")  # Show metric

        # Create two columns for side-by-side comparison
        col1, col2 = st.columns(2)  # Split into 2 columns

        # Left column: Baseline emissions
        with col1:  # Work inside left column
            st.subheader("Baseline Emissions")  # Column title

            # Display baseline values
            st.markdown(f"**Car:** {baseline.get('car', 0):.2f} g CO2")  # Car emissions
            st.markdown(f"**Bus:** {baseline.get('bus', 0):.2f} g CO2")  # Bus emissions
            st.markdown(f"**Truck:** {baseline.get('truck', 0):.2f} g CO2")  # Truck emissions
            st.markdown(f"**Motorcycle:** {baseline.get('motorcycle', 0):.2f} g CO2")  # Motorcycle emissions
            st.markdown(f"**Total:** {baseline.get('total', 0):.2f} g CO2")  # Total emissions

        # Right column: EV scenario emissions
        with col2:  # Work inside right column
            st.subheader("EV Scenario Emissions")  # Column title

            # Display EV scenario values
            st.markdown(f"**Car:** {ev_scenario.get('car', 0):.2f} g CO2")  # Car emissions
            st.markdown(f"**Bus:** {ev_scenario.get('bus', 0):.2f} g CO2")  # Bus emissions
            st.markdown(f"**Truck:** {ev_scenario.get('truck', 0):.2f} g CO2")  # Truck emissions
            st.markdown(f"**Motorcycle:** {ev_scenario.get('motorcycle', 0):.2f} g CO2")  # Motorcycle emissions
            st.markdown(f"**Total:** {ev_scenario.get('total', 0):.2f} g CO2")  # Total emissions

        # Create comparison bar chart
        st.subheader("Comparison Chart")  # Chart section title

        # Prepare data for chart
        chart_data = {
            "Baseline": baseline.get("total", 0),  # Baseline total
            "EV Scenario": ev_scenario.get("total", 0),  # EV scenario total
        }

        # Create bar chart
        st.bar_chart(chart_data)  # Show comparison bar chart

        # Add note explaining the assumption
        st.info("EV Scenario Assumption: 30% of cars are replaced with electric vehicles that produce 0 g/km tailpipe emissions.")  # Info box
    else:
        st.warning("output/emissions.json not found. Run emissions.py first to generate emissions data.")  # Warning if file missing

# --- Step 8: Add footer ---
st.markdown("---")  # Separator line
st.caption("Author: Hafsa | Portfolio Project | Vision-Based Vehicle Detection for Street-Level Emissions Mapping")  # Footer text
