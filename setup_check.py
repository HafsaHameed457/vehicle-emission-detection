# setup_check.py - Downloads YOLOv8n model and verifies vehicle classes exist

# Import the YOLO class from ultralytics library
from ultralytics import YOLO

# Download and load the YOLOv8n model (n = nano, smallest and fastest variant)
# The model file (yolov8n.pt) will be downloaded automatically on first run
model = YOLO("yolov8n.pt")

# Print confirmation that the model loaded successfully
print("=" * 50)
print("YOLOv8n model loaded successfully!")
print("=" * 50)

# Get the class names dictionary from the model (maps class IDs to names)
class_names = model.names

# Print all class names so we can verify vehicle classes exist
print("\nAll COCO class names:")
for class_id, name in class_names.items():
    print(f"  {class_id}: {name}")

# Define the vehicle class IDs we care about for this project
# These are the standard COCO dataset IDs for vehicles
vehicle_classes = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

# Verify each vehicle class exists in the model
print("\nVerifying vehicle classes:")
for class_id, expected_name in vehicle_classes.items():
    # Check if this class ID exists in the model's class names
    if class_id in class_names:
        actual_name = class_names[class_id]
        print(f"  [OK] Class {class_id}: {actual_name}")
    else:
        print(f"  [MISSING] Class {class_id}: {expected_name} not found!")

print("\nSetup check complete. Model is ready for vehicle detection.")
