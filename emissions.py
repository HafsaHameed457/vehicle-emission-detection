# emissions.py — Estimate CO2 and NOx emissions from vehicle counts
# This script reads the vehicle counts from output/all_counts.json,
# applies emission factors per vehicle type, and calculates
# total estimated emissions for each video.

# --- Step 1: Import required libraries ---
import json  # For reading the counts JSON file
import os  # For file path operations

# --- Step 2: Define emission factors (grams per vehicle per km) ---
# These are approximate average emission factors from literature
# Source: EEA (European Environment Agency) and EPA guidelines
EMISSION_FACTORS = {
    "car": {
        "co2": 120.0,  # Average car emits ~120g CO2 per km
        "nox": 0.05,   # Average car emits ~0.05g NOx per km
    },
    "motorcycle": {
        "co2": 80.0,   # Average motorcycle emits ~80g CO2 per km
        "nox": 0.03,   # Average motorcycle emits ~0.03g NOx per km
    },
    "bus": {
        "co2": 650.0,  # Average bus emits ~650g CO2 per km
        "nox": 3.5,    # Average bus emits ~3.5g NOx per km
    },
    "truck": {
        "co2": 800.0,  # Average truck emits ~800g CO2 per km
        "nox": 4.0,    # Average truck emits ~4.0g NOx per km
    },
}

# --- Step 3: Define average trip distance per vehicle (km) ---
# This is an assumption — adjust based on your study area
AVG_TRIP_DISTANCE_KM = 5.0  # Assume each vehicle travels ~5 km in the video

# --- Step 4: Define file paths ---
COUNTS_FILE = os.path.join("output", "all_counts.json")  # Input: vehicle counts
OUTPUT_FILE = os.path.join("output", "emissions.json")  # Output: emission estimates

# --- Step 5: Read vehicle counts from JSON file ---
with open(COUNTS_FILE, "r") as f:  # Open the counts file for reading
    all_counts = json.load(f)  # Load JSON data into a Python dictionary

# --- Step 6: Dictionary to store emission results ---
emissions_results = {}  # Will store {video_name: {vehicle_type: {co2, nox}}}

# --- Step 7: Loop through each video's counts ---
for video_name, vehicle_counts in all_counts.items():  # Iterate over each video
    print(f"\nCalculating emissions for: {video_name}")

    # Initialize dictionary for this video's emissions
    video_emissions = {
        "car": {"co2_g": 0.0, "nox_g": 0.0},  # Start with zero for car
        "motorcycle": {"co2_g": 0.0, "nox_g": 0.0},  # Start with zero for motorcycle
        "bus": {"co2_g": 0.0, "nox_g": 0.0},  # Start with zero for bus
        "truck": {"co2_g": 0.0, "nox_g": 0.0},  # Start with zero for truck
    }

    # --- Step 8: Loop through each vehicle type ---
    for vehicle_type, count in vehicle_counts.items():  # Iterate over vehicle types
        if count > 0:  # Only calculate if there are vehicles of this type
            # Get emission factors for this vehicle type
            factors = EMISSION_FACTORS[vehicle_type]  # Look up CO2 and NOx factors

            # Calculate total emissions = count * factor * distance
            co2_total = count * factors["co2"] * AVG_TRIP_DISTANCE_KM  # Total CO2 in grams
            nox_total = count * factors["nox"] * AVG_TRIP_DISTANCE_KM  # Total NOx in grams

            # Store results
            video_emissions[vehicle_type]["co2_g"] = co2_total  # Save CO2
            video_emissions[vehicle_type]["nox_g"] = nox_total  # Save NOx

            print(f"  {vehicle_type:12s}: {count:3d} vehicles -> CO2: {co2_total:,.0f}g, NOx: {nox_total:.2f}g")

    # --- Step 9: Calculate totals for this video ---
    total_co2 = sum(v["co2_g"] for v in video_emissions.values())  # Sum all CO2
    total_nox = sum(v["nox_g"] for v in video_emissions.values())  # Sum all NOx

    # Add totals to the results
    video_emissions["total"] = {"co2_g": total_co2, "nox_g": total_nox}  # Store totals

    print(f"  {'TOTAL':12s}: CO2: {total_co2:,.0f}g, NOx: {total_nox:.2f}g")

    # Store this video's results
    emissions_results[video_name] = video_emissions  # Add to master dictionary

# --- Step 10: Save emission results to JSON file ---
with open(OUTPUT_FILE, "w") as f:  # Open output file for writing
    json.dump(emissions_results, f, indent=2)  # Write results as formatted JSON

# --- Step 11: Print final summary ---
print(f"\n{'='*60}")
print("EMISSIONS SUMMARY")
print(f"{'='*60}")
print(f"Assuming average trip distance: {AVG_TRIP_DISTANCE_KM} km per vehicle")
print(f"Results saved to: {OUTPUT_FILE}")
print(f"{'='*60}")
