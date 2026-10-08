# detect.py — Vehicle Detection, Tracking, and Counting Pipeline
# This script uses YOLOv8n to detect vehicles in a traffic video,
# assigns each vehicle a unique tracking ID, counts unique vehicles
# per type, and saves an annotated video + JSON counts file.

# --- Step 1: Import required libraries ---
import cv2  # OpenCV for video capture, drawing, and writing
import json  # For saving counts to a JSON file
import os  # For creating directories and checking file paths
from ultralytics import YOLO  # YOLOv8 model from Ultralytics

# --- Step 2: Define vehicle class IDs and names ---
# COCO dataset class IDs for vehicles we care about
VEHICLE_CLASSES = {
    2: "car",  # Class ID 2 = car
    3: "motorcycle",  # Class ID 3 = motorcycle
    5: "bus",  # Class ID 5 = bus
    7: "truck",  # Class ID 7 = truck
}

# --- Step 3: Define file paths ---
VIDEO_PATH = os.path.join("data", "traffic.mp4")  # Input video path
OUTPUT_VIDEO = os.path.join("output", "annotated.mp4")  # Output annotated video path
OUTPUT_JSON = os.path.join("output", "counts.json")  # Output counts JSON path

# --- Step 4: Create output directory if it doesn't exist ---
os.makedirs("output", exist_ok=True)  # exist_ok=True prevents error if folder already exists

# --- Step 5: Load the YOLOv8n model ---
# YOLOv8n is the "nano" version — smallest and fastest, good for CPU
model = YOLO("yolov8n.pt")  # Loads the pre-trained YOLOv8n weights (auto-downloads if missing)

# --- Step 6: Open the input video with OpenCV ---
cap = cv2.VideoCapture(VIDEO_PATH)  # Open video file for reading

# Check if video opened successfully
if not cap.isOpened():
    print(f"ERROR: Cannot open video at {VIDEO_PATH}")
    print("Make sure data/traffic.mp4 exists.")
    exit(1)  # Exit with error code 1

# --- Step 7: Get video properties for the output writer ---
fps = int(cap.get(cv2.CAP_PROP_FPS))  # Frames per second of input video
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Frame width in pixels
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Frame height in pixels
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total number of frames

print(f"Video: {width}x{height} @ {fps}fps, {total_frames} frames")

# --- Step 8: Create VideoWriter to save annotated output ---
# fourcc is a 4-character code for video codec — "mp4v" is widely compatible
fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Create codec object for MP4
out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, (width, height))  # Initialize video writer

# --- Step 9: Initialize tracking data structures ---
# Dictionary to store unique track IDs per vehicle type
# Keys are vehicle names, values are sets of track IDs (sets auto-deduplicate)
unique_counts = {
    "car": set(),  # Set of unique car track IDs seen so far
    "motorcycle": set(),  # Set of unique motorcycle track IDs
    "bus": set(),  # Set of unique bus track IDs
    "truck": set(),  # Set of unique truck track IDs
}

# --- Step 10: Process video frame by frame ---
frame_num = 0  # Counter to track which frame we're on

while True:  # Loop until video ends
    ret, frame = cap.read()  # Read next frame; ret=True if successful, frame=image data

    if not ret:  # If ret is False, we've reached the end of the video
        break  # Exit the loop

    frame_num += 1  # Increment frame counter
    print(f"Processing frame {frame_num}/{total_frames}...", end="\r")  # Print progress (overwrite line)

    # --- Step 11: Run YOLOv8 tracking on this frame ---
    # persist=True keeps track IDs consistent across frames
    # verbose=False suppresses per-frame console output from ultralytics
    results = model.track(frame, persist=True, verbose=False)

    # --- Step 12: Extract detection results ---
    boxes = results[0].boxes  # Get bounding box results from first (and only) image

    # --- Step 13: Check if any detections exist ---
    if boxes is not None and len(boxes) > 0:  # If there are detections
        # --- Step 14: Loop through each detected box ---
        for i in range(len(boxes)):  # Iterate over all detected objects
            class_id = int(boxes.cls[i])  # Get the class ID of this detection (as integer)

            # --- Step 15: Filter — only keep vehicle classes ---
            if class_id in VEHICLE_CLASSES:  # If this is a car, motorcycle, bus, or truck
                vehicle_name = VEHICLE_CLASSES[class_id]  # Get human-readable name (e.g., "car")

                # --- Step 16: Get tracking ID ---
                # boxes.id contains the track ID assigned by the tracker
                # It can be None if tracking failed or no ID assigned
                if boxes.id is not None:  # If tracking IDs are available
                    track_id = int(boxes.id[i])  # Get the track ID for this detection
                else:
                    track_id = -1  # Use -1 as fallback when no tracking ID exists

                # --- Step 17: Add track ID to the unique set for this vehicle type ---
                unique_counts[vehicle_name].add(track_id)  # Set automatically ignores duplicates

                # --- Step 18: Get bounding box coordinates ---
                x1, y1, x2, y2 = boxes.xyxy[i]  # Get box corners: top-left (x1,y1), bottom-right (x2,y2)
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # Convert from float to int for drawing

                # --- Step 19: Draw bounding box on the frame ---
                # Color: green (BGR format: 0,255,0), thickness: 2 pixels
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # --- Step 20: Create label text with vehicle type and track ID ---
                label = f"{vehicle_name} #{track_id}"  # e.g., "car #12"

                # --- Step 21: Draw label background rectangle for readability ---
                (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(frame, (x1, y1 - 25), (x1 + text_w, y1), (0, 255, 0), -1)  # Filled green box

                # --- Step 22: Draw label text on the frame ---
                cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    # --- Step 23: Write the annotated frame to output video ---
    out.write(frame)  # Save this frame (with boxes drawn) to the output video

# --- Step 24: Release video resources ---
cap.release()  # Close the input video
out.release()  # Close and save the output video
print()  # Print newline after progress line

# --- Step 25: Convert sets to counts (number of unique IDs per type) ---
final_counts = {}
for vehicle_name, id_set in unique_counts.items():  # Loop through each vehicle type
    final_counts[vehicle_name] = len(id_set)  # Count = number of unique track IDs

# --- Step 26: Save counts to JSON file ---
with open(OUTPUT_JSON, "w") as f:  # Open JSON file for writing
    json.dump(final_counts, f, indent=2)  # Write counts as formatted JSON

# --- Step 27: Print final counts to terminal ---
print("=" * 40)
print("VEHICLE COUNT RESULTS")
print("=" * 40)
for vehicle_name, count in final_counts.items():  # Loop through each vehicle type
    print(f"  {vehicle_name:12s}: {count}")  # Print name and count with alignment
print("=" * 40)
print(f"Annotated video saved to: {OUTPUT_VIDEO}")
print(f"Counts JSON saved to: {OUTPUT_JSON}")
