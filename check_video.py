# check_video.py - Opens traffic.mp4, prints properties, extracts sample frames

# Import OpenCV for video processing
import cv2

# Import os for path operations
import os

# Define the path to the video file
video_path = os.path.join("data", "traffic.mp4")

# Check if the video file exists before trying to open it
if not os.path.exists(video_path):
    print(f"ERROR: Video file not found at {video_path}")
    print("Please place your traffic video in the data/ folder as traffic.mp4")
    exit(1)

# Open the video file using OpenCV's VideoCapture
cap = cv2.VideoCapture(video_path)

# Check if the video opened successfully
if not cap.isOpened():
    print(f"ERROR: Could not open video file {video_path}")
    exit(1)

# Get video properties using OpenCV's get() method with property constants
fps = cap.get(cv2.CAP_PROP_FPS)              # Frames per second
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total number of frames
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))   # Frame width in pixels
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Frame height in pixels

# Calculate duration in seconds (total frames divided by frames per second)
duration = frame_count / fps if fps > 0 else 0

# Print all video properties
print("=" * 50)
print("Video Properties:")
print("=" * 50)
print(f"  File: {video_path}")
print(f"  Resolution: {width} x {height}")
print(f"  FPS: {fps:.2f}")
print(f"  Total frames: {frame_count}")
print(f"  Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
print("=" * 50)

# Define which frame numbers to extract as samples
# We pick frames at 25%, 50%, and 75% through the video
sample_frames = [int(frame_count * 0.25), int(frame_count * 0.50), int(frame_count * 0.75)]

# Loop through the 3 sample positions
for i, frame_num in enumerate(sample_frames, start=1):
    # Set the video position to the specific frame number
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

    # Read the frame at the current position
    ret, frame = cap.read()

    # Check if the frame was read successfully
    if ret:
        # Define the output filename for this sample frame
        output_path = os.path.join("output", f"sample_frame_{i}.jpg")

        # Save the frame as a JPEG image
        cv2.imwrite(output_path, frame)

        # Print confirmation
        print(f"  Saved sample frame {i} (frame {frame_num}) to {output_path}")
    else:
        print(f"  WARNING: Could not read frame {frame_num}")

# Release the video capture object to free up system resources
cap.release()

print("\nSample frames extracted successfully!")
