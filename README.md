# Vision-Based Vehicle Detection for Street-Level Emissions Mapping

## Overview

This project detects vehicles in traffic videos using YOLO (You Only Look Once) deep learning, estimates CO2 and NOx emissions based on vehicle class, and visualizes the results on an interactive map and dashboard.

## Features

- **Vehicle Detection**: Uses YOLOv8 to detect and track cars, motorcycles, buses, and trucks in traffic videos
- **Emissions Estimation**: Calculates CO2 and NOx emissions based on vehicle class and average trip distance
- **Interactive Map**: Folium heatmap showing emission hotspots across different locations
- **Streamlit Dashboard**: Web-based interface for exploring vehicle counts, emissions data, and the map

## Project Structure

```
vision-based-vehicle-detection-for-street-level-emission/
├── data/                    # Input traffic videos (7 videos)
├── output/
│   ├── annotated_videos/    # Videos with bounding boxes and tracking IDs
│   ├── all_counts.json      # Vehicle counts per video
│   ├── emissions.json       # CO2/NOx emissions per video
│   └── emissions_map.html   # Interactive Folium heatmap
├── detect.py                # Main detection/tracking/counting pipeline
├── emissions.py             # Emissions calculation from vehicle counts
├── map.py                   # Folium heatmap generation
├── app.py                   # Streamlit dashboard
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Setup

### Prerequisites

- Python 3.12 (3.14 may cause DLL errors with PyTorch)
- Windows OS

### Installation

1. Create a virtual environment:
   ```powershell
   python -m venv venv
   ```

2. Activate the virtual environment:
   ```powershell
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage

### Step 1: Run Vehicle Detection

Processes all videos in the `data/` folder, detects vehicles using YOLOv8, tracks them across frames, and saves annotated videos and JSON counts.

```powershell
venv\Scripts\python.exe detect.py
```

**Output:**
- `output/annotated_videos/` — Videos with bounding boxes and tracking IDs
- `output/all_counts.json` — Vehicle counts per video

### Step 2: Calculate Emissions

Reads vehicle counts and calculates CO2/NOx emissions based on emission factors.

```powershell
venv\Scripts\python.exe emissions.py
```

**Output:**
- `output/emissions.json` — CO2 and NOx emissions per video

### Step 3: Generate Interactive Map

Creates a Folium heatmap showing emission hotspots.

```powershell
venv\Scripts\python.exe map.py
```

**Output:**
- `output/emissions_map.html` — Interactive heatmap (open in browser)

### Step 4: Launch Dashboard

Starts the Streamlit web dashboard.

```powershell
venv\Scripts\streamlit run app.py
```

**Access:** http://localhost:8501

## Vehicle Classes & Emission Factors

| Class | CO2 (g/km) | NOx (g/km) |
|-------|-----------|-----------|
| Car | 120 | 0.05 |
| Motorcycle | 80 | 0.015 |
| Bus | 650 | 0.55 |
| Truck | 800 | 1.0 |

**Assumption:** Average trip distance of 5 km per vehicle.

## Technology Stack

- **YOLOv8** (Ultralytics) — Object detection and tracking
- **OpenCV** — Video processing
- **Folium** — Interactive maps
- **Streamlit** — Web dashboard
- **Pandas/NumPy** — Data processing

## Limitations

- Detection accuracy depends on video quality, lighting, and occlusion
- Emission factors are simplified averages (real-world values vary by vehicle age, fuel type, driving conditions)
- GPS coordinates are placeholder values (in a real project, these would come from video metadata or manual input)
- Short video clips may not represent continuous traffic flow

## Future Work

- Integrate real GPS metadata from videos
- Add more vehicle classes (electric vehicles, hybrids)
- Use more accurate emission models (COPERT, MOVES)
- Deploy as a web service with live camera feeds
- Add temporal analysis (emissions by time of day)
