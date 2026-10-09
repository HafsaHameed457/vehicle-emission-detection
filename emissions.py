# emissions.py — Calculate CO2 emissions from vehicle counts
# This script reads output/all_counts.json, applies emission factors,
# and simulates an EV adoption scenario.

# --- Step 1: Import required libraries ---
import json  # For reading/writing JSON files
import os  # For file path operations

# --- Step 2: Define file paths ---
COUNTS_FILE = os.path.join("output", "all_counts.json")  # Input: vehicle counts
OUTPUT_FILE = os.path.join("output", "emissions.json")  # Output: emissions data

# --- Step 3: Define emission factors (g CO2 per km) ---
# These are average emission factors per vehicle class
EMISSION_FACTORS = {
    "car": 147,  # Average car emits 147g CO2/km
    "bus": 1071,  # Average bus emits 1071g CO2/km
    "truck": 800,  # Average truck emits 800g CO2/km
    "motorcycle": 120,  # Average motorcycle emits 120g CO2/km
}

# --- Step 4: Define trip distance assumption ---
# Each vehicle travels 0.1 km within camera view
TRIP_DISTANCE_KM = 0.1  # Distance in kilometers

# --- Step 5: Define EV scenario parameters ---
EV_REPLACEMENT_RATE = 0.30  # 30% of cars replaced with EVs
EV_EMISSION_FACTOR = 0  # EVs emit 0g CO2/km (tailpipe)

# --- Step 6: Load vehicle counts from JSON file ---
with open(COUNTS_FILE, "r") as f:  # Open counts file for reading
    counts_data = json.load(f)  # Load JSON data into a Python dictionary

# --- Step 7: Aggregate counts across all videos ---
# Initialize total counts for each vehicle type to 0
total_counts = {"car": 0, "bus": 0, "truck": 0, "motorcycle": 0}

# Loop through each video's counts and sum them up
for video_name, video_counts in counts_data.items():  # Iterate over each video
    for vehicle_type in total_counts:  # For each vehicle type
        # Add the count for this video, default to 0 if key missing
        total_counts[vehicle_type] += video_counts.get(vehicle_type, 0)

# --- Step 8: Calculate baseline emissions ---
# Initialize baseline emissions dictionary
baseline = {}

# Loop through each vehicle type and calculate emissions
for vehicle_type, count in total_counts.items():  # For each vehicle type
    # Emissions = count × distance × emission factor
    baseline[vehicle_type] = count * TRIP_DISTANCE_KM * EMISSION_FACTORS[vehicle_type]

# Calculate total baseline emissions
baseline["total"] = sum(baseline.values())  # Sum all vehicle type emissions

# --- Step 9: Calculate EV scenario emissions ---
# Initialize EV scenario emissions dictionary
ev_scenario = {}

# Loop through each vehicle type
for vehicle_type, count in total_counts.items():  # For each vehicle type
    if vehicle_type == "car":  # Only cars are affected by EV replacement
        # Calculate number of EVs (30% of cars)
        ev_count = count * EV_REPLACEMENT_RATE
        # Calculate remaining ICE cars (70% of cars)
        ice_count = count - ev_count
        # EV emissions: ICE cars emit normally, EVs emit 0
        ev_scenario[vehicle_type] = (ice_count * TRIP_DISTANCE_KM * EMISSION_FACTORS[vehicle_type]) + (ev_count * TRIP_DISTANCE_KM * EV_EMISSION_FACTOR)
    else:  # Other vehicle types unchanged
        ev_scenario[vehicle_type] = count * TRIP_DISTANCE_KM * EMISSION_FACTORS[vehicle_type]

# Calculate total EV scenario emissions
ev_scenario["total"] = sum(ev_scenario.values())  # Sum all vehicle type emissions

# --- Step 10: Calculate percent reduction ---
# Reduction = (baseline - ev_scenario) / baseline × 100
reduction_percent = ((baseline["total"] - ev_scenario["total"]) / baseline["total"]) * 100

# --- Step 11: Compile results into output dictionary ---
results = {
    "baseline": baseline,  # Baseline emissions by vehicle type
    "ev_scenario": ev_scenario,  # EV scenario emissions by vehicle type
    "reduction_percent": round(reduction_percent, 2),  # Percent reduction (rounded to 2 decimal places)
}

# --- Step 12: Save results to JSON file ---
with open(OUTPUT_FILE, "w") as f:  # Open output file for writing
    json.dump(results, f, indent=2)  # Write JSON data with indentation

# --- Step 13: Print summary table to terminal ---
print("=" * 60)  # Print separator line
print("EMISSIONS SUMMARY")  # Print title
print("=" * 60)  # Print separator line
print(f"Assuming trip distance: {TRIP_DISTANCE_KM} km per vehicle")  # Print distance assumption
print(f"EV replacement rate: {EV_REPLACEMENT_RATE * 100}% of cars")  # Print EV rate
print("-" * 60)  # Print separator line

# Print baseline emissions
print("BASELINE EMISSIONS:")  # Print section header
for vehicle_type, emission in baseline.items():  # For each vehicle type
    if vehicle_type != "total":  # Skip total for now
        print(f"  {vehicle_type:12s}: {emission:8.2f} g CO2")  # Print emission value
print(f"  {'TOTAL':12s}: {baseline['total']:8.2f} g CO2")  # Print total

print("-" * 60)  # Print separator line

# Print EV scenario emissions
print("EV SCENARIO EMISSIONS:")  # Print section header
for vehicle_type, emission in ev_scenario.items():  # For each vehicle type
    if vehicle_type != "total":  # Skip total for now
        print(f"  {vehicle_type:12s}: {emission:8.2f} g CO2")  # Print emission value
print(f"  {'TOTAL':12s}: {ev_scenario['total']:8.2f} g CO2")  # Print total

print("-" * 60)  # Print separator line
print(f"REDUCTION: {reduction_percent:.2f}%")  # Print percent reduction
print("=" * 60)  # Print separator line
print(f"Results saved to: {OUTPUT_FILE}")  # Print output file path
