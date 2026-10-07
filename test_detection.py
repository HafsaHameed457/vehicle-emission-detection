# test_detection.py - Runs YOLOv8 vehicle detection on a sample frame

# Import YOLO from ultralytics for object detection
from ultralytics import YOLO

# Import OpenCV for image reading, drawing, and saving
import cv2

# Import os for path operations
import os

# Import Counter from collections to count detections by type
from collections import Counter

# Define the path to the sample frame we want to test
# Using the first sample frame extracted by check_video.py
frame_path = os.path.join("output", "sample_frame_1.jpg")

# Check if the sample frame exists
if not os.path.exists(frame_path):
    print(f"ERROR: Sample frame not found at {frame_path}")
    print("Please run check_video.py first to extract sample frames.")
    exit(1)

# Load the YOLOv8n model (will use the already-downloaded yolov8n.pt)
print("Loading YOLOv8n model...")
model = YOLO("yolov8n.pt")
print("Model loaded.")

# Read the sample frame from disk using OpenCV
frame = cv2.imread(frame_path)

# Check if the frame was read successfully
if frame is None:
    print(f"ERROR: Could not read image {frame_path}")
    exit(1)

print(f"Running detection on {frame_path}...")

# Run YOLOv8 detection on the frame
# conf=0.25 means only keep detections with confidence >= 25%
# verbose=False suppresses the detailed per-frame output
results = model(frame, conf=0.25, verbose=False)

# Define the vehicle class IDs we want to filter for
# 2=car, 3=motorcycle, 5=bus, 7=truck
vehicle_class_ids = [2, 3, 5, 7]

# Get the class names dictionary from the model
class_names = model.names

# Initialize a list to store detection counts
detection_counts = Counter()

# Loop through all detection results (usually just 1 image)
for result in results:
    # Get the bounding boxes from the result
    boxes = result.boxes

    # Loop through each detected box
    for box in boxes:
        # Get the class ID for this detection
        class_id = int(box.cls[0])

        # Only process if this is a vehicle class we care about
        if class_id in vehicle_class_ids:
            # Get the class name
            class_name = class_names[class_id]

            # Increment the count for this vehicle type
            detection_counts[class_name] += 1

            # Get bounding box coordinates (x1, y1, x2, y2)
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            # Convert coordinates to integers for drawing
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Get the confidence score for this detection
            confidence = float(box.conf[0])

            # Draw a green bounding box around the detected vehicle
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Create a label string with class name and confidence
            label = f"{class_name} {confidence:.2f}"

            # Draw a filled rectangle behind the text for readability
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame, (x1, y1 - text_h - 10), (x1 + text_w, y1), (0, 255, 0), -1)

            # Draw the label text in black on top of the green rectangle
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

# Define the output path for the annotated image
output_path = os.path.join("output", "test_detection.jpg")

# Save the annotated frame with bounding boxes
cv2.imwrite(output_path, frame)

# Print detection results
print("\n" + "=" * 50)
print("Detection Results:")
print("=" * 50)

# Print count for each vehicle type
for vehicle_type in ["car", "motorcycle", "bus", "truck"]:
    count = detection_counts.get(vehicle_type, 0)
    print(f"  {vehicle_type}: {count}")

# Print total vehicle count
total = sum(detection_counts.values())
print(f"\n  Total vehicles detected: {total}")
print("=" * 50)

# Print the output file path
print(f"\nAnnotated image saved to: {output_path}")
