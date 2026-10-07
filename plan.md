```markdown
# plan.md

# Vision-Based Vehicle Detection for Street-Level Emissions Mapping
## 3-Day Sprint Plan

---

## Day 1: Detection & Counting Pipeline

### Goal
Working YOLOv8 pipeline that processes video, detects vehicles, tracks them, and counts by type.

### Tasks

**Hour 1-2: Setup & Data**
- Install: `pip install ultralytics opencv-python pandas numpy folium streamlit`
- Download a royalty-free traffic video (Pexels/Pixabay) or record 30-60 seconds on your phone
- Save as `data/traffic.mp4`
- Verify YOLOv8 works:
```python
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
results = model('data/traffic.mp4', save=True)
```

**Hour 3-5: Detection + Tracking + Counting**
- Write `detect.py`:
  - Load YOLOv8n
  - Filter classes: car (2), motorcycle (3), bus (5), truck (7)
  - Use `model.track(frame, persist=True)` for tracking
  - Count unique track IDs per vehicle type
  - Draw boxes + labels + count on output video
- Save output as `output/annotated.mp4`
- Save counts as `output/counts.json`:
```json
{"car": 45, "bus": 3, "truck": 8, "motorcycle": 12}
```

**Hour 6: Test & Fix**
- Run on full video
- Check: Are IDs stable? Are counts reasonable?
- Fix false positives (e.g., pedestrians) by filtering class IDs strictly

### Deliverable
- `detect.py`
- `output/annotated.mp4`
- `output/counts.json`

---

## Day 2: Emissions Estimation + Spatial Map

### Goal
Calculate CO₂ emissions from counts and visualize on interactive map.

### Tasks

**Hour 1-2: Emissions Model**
- Write `emissions.py`:
  - Load `counts.json`
  - Apply emission factors (g CO₂ per km):
    - Car: 147
    - Bus: 1071
    - Truck: 800
    - Motorcycle: 120
  - Assume each vehicle travels 0.1 km within camera view
  - Calculate total emissions per type
  - Add EV scenario: replace 30% of cars with EVs (0 g/km tailpipe)
- Output `output/emissions.json`:
```json
{
  "baseline": {"car": 661.5, "bus": 321.3, "truck": 640.0, "motorcycle": 144.0, "total": 1766.8},
  "ev_scenario": {"car": 463.05, "bus": 321.3, "truck": 640.0, "motorcycle": 144.0, "total": 1568.35},
  "reduction_percent": 11.2
}
```

**Hour 3-5: Spatial Map**
- Write `map.py`:
  - Define 5-10 grid cells around your camera location (use approximate lat/lon)
  - Distribute emissions across grid cells (simulate spatial spread)
  - Build Folium map with:
    - Circle markers sized by emissions
    - Color gradient (green → red)
    - Popup showing emission breakdown per cell
  - Add scenario toggle: two layers (baseline vs EV scenario) with LayerControl
- Save as `output/emissions_map.html`

**Hour 6: Test**
- Open map in browser
- Verify markers, colors, popups, layer toggle work

### Deliverable
- `emissions.py`
- `map.py`
- `output/emissions.json`
- `output/emissions_map.html`

---

## Day 3: Dashboard + Documentation

### Goal
Single Streamlit app tying everything together + README + demo video.

### Tasks

**Hour 1-3: Streamlit Dashboard**
- Write `app.py`:
  - Sidebar: upload video OR use default
  - Tab 1: Annotated video player
  - Tab 2: Emission counts table + bar chart
  - Tab 3: Folium map embedded
  - Tab 4: Scenario comparison (baseline vs EV)
- Run: `streamlit run app.py`
- Fix layout issues

**Hour 4: Demo Video**
- Screen record 2-3 minutes:
  - Show dashboard
  - Show detection video
  - Show map + scenario toggle
- Save as `demo.mp4`

**Hour 5-6: README + Cleanup**
- Write `README.md`:
  - Project overview
  - Methodology (detect → count → emissions → map)
  - Emission factors used
  - Limitations (single camera, fixed distance, tailpipe-only)
  - How to run
- Clean code: remove debug prints, add comments
- Push to GitHub

### Deliverable
- `app.py`
- `demo.mp4`
- `README.md`
- GitHub repository

---

## File Structure

```
project/
├── data/
│   └── traffic.mp4
├── output/
│   ├── annotated.mp4
│   ├── counts.json
│   ├── emissions.json
│   └── emissions_map.html
├── detect.py
├── emissions.py
├── map.py
├── app.py
├── requirements.txt
├── README.md
└── demo.mp4
```

---

## Requirements.txt

```
ultralytics
opencv-python
pandas
numpy
folium
streamlit
```

---

## Emission Factors Reference

| Vehicle Type | CO₂ (g/km) |
|-------------|-----------|
| Car | 147 |
| Bus | 1071 |
| Truck | 800 |
| Motorcycle | 120 |

Source: UNFCCC published factors

---

## Key Commands

```bash
# Detection
python detect.py

# Emissions
python emissions.py

# Map
python map.py

# Dashboard
streamlit run app.py
```

---

## Success Criteria

- [ ] Video processed with stable vehicle tracking
- [ ] Counts by type saved to JSON
- [ ] Emissions calculated for baseline + EV scenario
- [ ] Interactive Folium map with layer toggle
- [ ] Streamlit dashboard working
- [ ] Demo video recorded
- [ ] README complete
- [ ] GitHub repo pushed

---

## Application Framing (Use in Email/CV)

> "I built a vision-based vehicle detection pipeline using YOLOv8 that detects and classifies vehicles, estimates CO₂ emissions using published emission factors, and visualizes results on an interactive spatial map with scenario toggles. The project demonstrates the AI-based data acquisition and emissions estimation workflow relevant to community-scale emissions modelling."

---

## If Short on Time

**Priority order:**
1. Detection + counting (must have)
2. Emissions calculation (must have)
3. Folium map (must have)
4. Streamlit dashboard (nice to have)
5. Demo video (nice to have)

Skip dashboard if needed—static map + JSON is sufficient to show capability.
```