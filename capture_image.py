from picamera2 import Picamera2
from datetime import datetime
import os

# Create output folder
output_folder = "OutputImages"
os.makedirs(output_folder, exist_ok=True)

# Generate timestamp
timestamp = datetime.now().strftime("%d-%b-%Y-%H:%M:%S")
filename = f"{output_folder}/output_{timestamp}.png"

# Initialize and configure the camera
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1920, 1080)})
picam2.configure(config)
picam2.start()

# Capture and save the image
picam2.capture_file(filename)

print(f"Image saved as {filename}")
