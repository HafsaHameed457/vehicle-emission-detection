# Vision-Based Vehicle Detection for Street-Level Emissions Mapping

## Motivation

Urban transport is a major contributor to greenhouse gas emissions and air pollution. Traditional emissions models rely on aggregate traffic data and cannot capture street-level variations. This project demonstrates how computer vision and deep learning can be used to detect individual vehicles in traffic videos and estimate emissions at a granular level, enabling more targeted urban planning and sustainability interventions.

## What This Project Does

- Detects vehicles (cars, motorcycles, buses, trucks) in traffic videos using YOLOv8
- Tracks vehicles across video frames to avoid double-counting
- Estimates CO2 emissions based on vehicle class and distance travelled
- Simulates an EV adoption scenario and calculates emission reductions
- Visualizes emissions on an interactive map with grid-based spatial distribution
- Provides a Streamlit dashboard for exploring results

## Pipeline Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Traffic Videos │────▶│  YOLOv8 Detect  │────▶│  Vehicle Counts │
│  (data/)        │     │  + Track        │     │  (JSON)         │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Interactive    │◀────│  Folium Map     │◀────│  Emissions      │
│  Dashboard      │     │  (Grid + Layers)│     │  (Baseline/EV)  │
│  (Streamlit)    │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Technical Stack

| Tool | Purpose |
|------|---------|
| Python 3.12 | Programming language |
| YOLOv8 (Ultralytics) | Object detection and tracking |
| OpenCV | Video processing |
| Folium | Interactive maps |
| Streamlit | Web dashboard |
| Pandas | Data manipulation |
| NumPy | Numerical operations |

## Emission Factors Used

| Vehicle Class | CO2 (g/km) | Source |
|---------------|-----------|--------|
| Car | 147 | EPA average passenger vehicle |
| Bus | 1071 | EPA average transit bus |
| Truck | 800 | EPA average heavy-duty truck |
| Motorcycle | 120 | EPA average motorcycle |

**Assumption:** Each vehicle travels 0.1 km within camera view.

## Key Features

- Real-time vehicle detection and tracking with YOLOv8
- Support for 4 vehicle classes: car, motorcycle, bus, truck
- Emissions calculation with baseline and EV scenario comparison
- Interactive Folium map with color-coded grid cells
- Layer control to toggle between scenarios
- Streamlit dashboard with 4 tabs for comprehensive visualization
- Graceful handling of missing files

## Limitations

- Detection accuracy depends on video quality, lighting, and occlusion
- Emission factors are simplified averages (real-world values vary by vehicle age, fuel type, driving conditions)
- GPS coordinates are placeholder values (in a real project, these would come from video metadata)
- Short video clips may not represent continuous traffic flow
- Grid-based spatial distribution is simulated, not based on actual camera locations
- Only CO2 is estimated; other pollutants (NOx, PM) are not included

## Relevance to Research

This project connects to urban emissions modelling and digital twin research by:

- Demonstrating how computer vision can provide granular, street-level emissions data
- Enabling scenario analysis (e.g., EV adoption) for policy evaluation
- Providing a framework for integrating real-time traffic data into urban digital twins
- Supporting research on sustainable transport and smart city initiatives

## How to Run

### Prerequisites

- Python 3.12 (3.14 may cause DLL errors with PyTorch)
- Windows, Mac, or Linux

### Setup

```powershell
# Clone the repository
git clone https://github.com/yourusername/vision-based-vehicle-detection.git
cd vision-based-vehicle-detection

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run the Pipeline

```powershell
# Step 1: Detect vehicles in all videos
python detect.py

# Step 2: Calculate emissions
python emissions.py

# Step 3: Generate interactive map
python map.py

# Step 4: Launch dashboard
streamlit run app.py
```

## File Structure

```
vision-based-vehicle-detection/
├── data/                      # Input traffic videos
├── output/
│   ├── annotated_videos/      # Videos with bounding boxes and tracking IDs
│   ├── all_counts.json        # Vehicle counts per video
│   ├── emissions.json         # CO2 emissions (baseline + EV scenario)
│   └── emissions_map.html     # Interactive Folium map
├── detect.py                  # Vehicle detection and tracking
├── emissions.py               # Emissions calculation
├── map.py                     # Map generation
├── app.py                     # Streamlit dashboard
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Sample Output

- **Annotated Videos**: Videos with bounding boxes around detected vehicles, class labels, and tracking IDs
- **Counts JSON**: Vehicle counts per video (e.g., `{"car": 25, "bus": 3, "truck": 5}`)
- **Emissions JSON**: Baseline and EV scenario emissions with percent reduction
- **Interactive Map**: Folium map with color-coded circle markers showing emission intensity
- **Dashboard**: Streamlit app with 4 tabs for video, counts, map, and scenario comparison

## Future Work

- Integrate real GPS metadata from videos
- Add more vehicle classes (electric vehicles, hybrids)
- Use more accurate emission models (COPERT, MOVES)
- Deploy as a web service with live camera feeds
- Add temporal analysis (emissions by time of day)
- Include other pollutants (NOx, PM2.5)
- Add user input for custom emission factors and scenarios

## Author

**Hafsa**
- LinkedIn: [your-linkedin-profile]
- Portfolio: [your-portfolio-website]

## License

MIT License — feel free to use this project for research and educational purposes.
