# detect.py — Vehicle Detection, Tracking, and Counting Pipeline (Multi-Video)
# This script uses YOLOv8n to detect vehicles in ALL traffic videos in data/,
# assigns each vehicle a unique tracking ID, counts unique vehicles
# per type, and saves annotated videos + JSON counts for each.

# --- Step 1: Import required libraries ---
import cv2  # OpenCV for video capture, drawing, and writing
import json  # For saving counts to a JSON file
import os  # For creating directories and checking file paths
import glob  # For finding all video files in a directory
from ultralytics import YOLO  # YOLOv8 model from Ultralytics

# --- Step 2: Define vehicle class IDs and names ---
# COCO dataset class IDs for vehicles we care about
VEHICLE_CLASSES = {
    2: "car",  # Class ID 2 = car
    3: "motorcycle",  # Class ID 3 = motorcycle
    5: "bus",  # Class ID 5 = bus
    7: "truck",  # Class ID 7 = truck
}

# --- Step 3: Define folder paths ---
DATA_DIR = "data"  # Folder containing input videos
OUTPUT_DIR = "output"  # Folder for annotated videos and JSON files

# --- Step 4: Create output directory if it doesn't exist ---
os.makedirs(OUTPUT_DIR, exist_ok=True)  # exist_ok=True prevents error if folder already exists

# --- Step 5: Find all video files in the data folder ---
# glob.glob returns all files matching the pattern (e.g., *.mp4, *.avi, *.mov)
video_extensions = ["*.mp4", "*.avi", "*.mov", "*.mkv"]  # Supported video formats
video_files = []  # Empty list to store all found video paths
for ext in video_extensions:  # Loop through each extension pattern
    video_files.extend(glob.glob(os.path.join(DATA_DIR, ext)))  # Add matching files to list

# --- Step 6: Check if any videos were found ---
if len(video_files) == 0:  # If no videos found
    print(f"ERROR: No video files found in '{DATA_DIR}/' folder.")
    print("Supported formats: .mp4, .avi, .mov, .mkv")
    exit(1)  # Exit with error code 1

print(f"Found {len(video_files)} video(s) to process:")
for vf in video_files:  # Loop through found videos
    print(f"  - {vf}")  # Print each video path
print()

# --- Step 7: Load the YOLOv8n model ---
# YOLOv8n is the "nano" version — smallest and fastest, good for CPU
model = YOLO("yolov8n.pt")  # Loads the pre-trained YOLOv8n weights (auto-downloads if missing)

# --- Step 8: Dictionary to store counts for ALL videos ---
all_counts = {}  # Will store {video_name: {vehicle_type: count}}

# --- Step 9: Loop through each video file ---
for video_path in video_files:  # Process one video at a time
    video_name = os.path.basename(video_path)  # Get just the filename (e.g., "traffic.mp4")
    print(f"\n{'='*50}")
    print(f"Processing: {video_name}")
    print(f"{'='*50}")

    # --- Step 10: Open the input video with OpenCV ---
    cap = cv2.VideoCapture(video_path)  # Open video file for reading

    # Check if video opened successfully
    if not cap.isOpened():  # If video failed to open
        print(f"  WARNING: Cannot open {video_name}, skipping...")
        continue  # Skip to next video

    # --- Step 11: Get video properties for the output writer ---
    fps = int(cap.get(cv2.CAP_PROP_FPS))  # Frames per second of input video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Frame width in pixels
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Frame height in pixels
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total number of frames

    print(f"  Resolution: {width}x{height} @ {fps}fps, {total_frames} frames")

    # --- Step 12: Define output paths for this video ---
    # Create output video name by adding "_annotated" before the extension
    name_without_ext = os.path.splitext(video_name)[0]  # e.g., "traffic" from "traffic.mp4"
    output_video_name = f"{name_without_ext}_annotated.mp4"  # e.g., "traffic_annotated.mp4"
    output_video_path = os.path.join(OUTPUT_DIR, output_video_name)  # Full output path
    output_json_name = f"{name_without_ext}_counts.json"  # e.g., "traffic_counts.json"
    output_json_path = os.path.join(OUTPUT_DIR, output_json_name)  # Full JSON path

    # --- Step 13: Create VideoWriter to save annotated output ---
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Create codec object for MP4
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))  # Initialize writer

    # --- Step 14: Initialize tracking data structures for THIS video ---
    unique_counts = {
        "car": set(),  # Set of unique car track IDs seen so far
        "motorcycle": set(),  # Set of unique motorcycle track IDs
        "bus": set(),  # Set of unique bus track IDs
        "truck": set(),  # Set of unique truck track IDs
    }

    # --- Step 15: Process video frame by frame ---
    frame_num = 0  # Counter to track which frame we're on

    while True:  # Loop until video ends
        ret, frame = cap.read()  # Read next frame; ret=True if successful

        if not ret:  # If ret is False, we've reached the end of the video
            break  # Exit the loop

        frame_num += 1  # Increment frame counter
        print(f"  Frame {frame_num}/{total_frames}...", end="\r")  # Print progress

        # --- Step 16: Run YOLOv8 tracking on this frame ---
        # persist=True keeps track IDs consistent across frames
        # verbose=False suppresses per-frame console output
        results = model.track(frame, persist=True, verbose=False)

        # --- Step 17: Extract detection results ---
        boxes = results[0].boxes  # Get bounding box results

        # --- Step 18: Check if any detections exist ---
        if boxes is not None and len(boxes) > 0:  # If there are detections
            # --- Step 19: Loop through each detected box ---
            for i in range(len(boxes)):  # Iterate over all detected objects
                class_id = int(boxes.cls[i])  # Get the class ID of this detection

                # --- Step 20: Filter — only keep vehicle classes ---
                if class_id in VEHICLE_CLASSES:  # If this is a car, motorcycle, bus, or truck
                    vehicle_name = VEHICLE_CLASSES[class_id]  # Get human-readable name

                    # --- Step 21: Get tracking ID ---
                    if boxes.id is not None:  # If tracking IDs are available
                        track_id = int(boxes.id[i])  # Get the track ID
                    else:
                        track_id = -1  # Fallback when no tracking ID exists

                    # --- Step 22: Add track ID to the unique set ---
                    unique_counts[vehicle_name].add(track_id)  # Set auto-deduplicates

                    # --- Step 23: Get bounding box coordinates ---
                    x1, y1, x2, y2 = boxes.xyxy[i]  # Get box corners
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # Convert to int

                    # --- Step 24: Draw bounding box on the frame ---
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green box

                    # --- Step 25: Create label text ---
                    label = f"{vehicle_name} #{track_id}"  # e.g., "car #12"

                    # --- Step 26: Draw label background ---
                    (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(frame, (x1, y1 - 25), (x1 + text_w, y1), (0, 255, 0), -1)

                    # --- Step 27: Draw label text ---
                    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        # --- Step 28: Write the annotated frame to output video ---
        out.write(frame)  # Save this frame to the output video

    # --- Step 29: Release video resources for THIS video ---
    cap.release()  # Close the input video
    out.release()  # Close and save the output video
    print()  # Newline after progress

    # --- Step 30: Convert sets to counts for THIS video ---
    video_counts = {}
    for vehicle_name, id_set in unique_counts.items():  # Loop through each vehicle type
        video_counts[vehicle_name] = len(id_set)  # Count = number of unique track IDs

    # --- Step 31: Save counts to JSON file for THIS video ---
    with open(output_json_path, "w") as f:  # Open JSON file for writing
        json.dump(video_counts, f, indent=2)  # Write counts as formatted JSON

    # --- Step 32: Store in master counts dictionary ---
    all_counts[video_name] = video_counts  # Save this video's counts

    # --- Step 33: Print results for THIS video ---
    print(f"  Results for {video_name}:")
    for vehicle_name, count in video_counts.items():  # Loop through each type
        print(f"    {vehicle_name:12s}: {count}")  # Print name and count
    print(f"  Annotated video: {output_video_path}")
    print(f"  Counts JSON: {output_json_path}")

# --- Step 34: Save combined counts for ALL videos ---
combined_json_path = os.path.join(OUTPUT_DIR, "all_counts.json")  # Path for combined results
with open(combined_json_path, "w") as f:  # Open combined JSON file
    json.dump(all_counts, f, indent=2)  # Write all video counts

# --- Step 35: Print final summary ---
print(f"\n{'='*50}")
print("FINAL SUMMARY — ALL VIDEOS")
print(f"{'='*50}")
for video_name, counts in all_counts.items():  # Loop through each video
    print(f"\n  {video_name}:")
    for vehicle_name, count in counts.items():  # Loop through each vehicle type
        print(f"    {vehicle_name:12s}: {count}")  # Print count
print(f"\n{'='*50}")
print(f"Combined counts saved to: {combined_json_path}")
print("Done!")
