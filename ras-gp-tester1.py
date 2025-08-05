"""
Simple GCP Detection Tester
==========================
Test a YOLO model for Ground Control Point detection on images.

Instructions:
1. Update the paths below to your image and model files
2. Run: python gcp_test.py

Requirements: ultralytics, opencv-python, numpy, Pillow
"""

import tempfile
from pathlib import Path
import numpy as np
from PIL import Image
from ultralytics import YOLO
import time

# =============================================================================
# UPDATE THESE PATHS TO YOUR FILES
# =============================================================================
IMAGE_PATH = "test.png"  # Path to your image file
MODEL_PATH = "best.pt"  # Path to the YOLO model file


# =============================================================================


def load_image(image_path, channel=2):
    """Load image and extract specified channel (0=Red, 1=Green, 2=Blue)."""
    arr = np.array(Image.open(image_path))

    if arr.ndim == 3 and arr.shape[2] > channel:
        channel_data = arr[:, :, channel]
    elif arr.ndim == 2:
        channel_data = arr
    else:
        channel_data = arr[:, :, -1] if arr.ndim == 3 else arr

    # Convert to uint8 and make 3-channel
    if channel_data.dtype != np.uint8:
        channel_data = ((channel_data - channel_data.min()) /
                        (channel_data.max() - channel_data.min()) * 255).astype(np.uint8)

    return np.stack([channel_data] * 3, axis=2)


def test_gcp_detection(image_path, model_path, channel=2):
    """Test GCP detection on image."""
    # Load model and image
    model = YOLO(model_path)
    image = load_image(image_path, channel)

    # Save temporary file for YOLO
    temp_path = tempfile.mktemp(suffix='.jpg')
    Image.fromarray(image).save(temp_path, 'JPEG', quality=95)

    try:
        # Test multiple confidence levels
        for conf in [0.25, 0.1, 0.05, 0.01]:
            results = model(temp_path, conf=conf, verbose=False)
            detections = results[0].boxes

            if detections is not None and len(detections) > 0:
                print(f"✅ GCP DETECTED: Found {len(detections)} GCP(s) with confidence ≥ {conf}")
                return True

        print("❌ NO GCP DETECTED")
        return False

    finally:
        # Clean up temp file
        try:
            Path(temp_path).unlink()
        except:
            pass

LOG_FILE = "test.txt"

def log_to_file(message):
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

while True:
    if not Path(IMAGE_PATH).exists():
        msg1 = f"❌ Image file not found: {IMAGE_PATH}"
        msg2 = "   Please update IMAGE_PATH in the script"
        print(msg1)
        print(msg2)
        log_to_file(msg1)
        log_to_file(msg2)
        exit(1)

    if not Path(MODEL_PATH).exists():
        msg1 = f"❌ Model file not found: {MODEL_PATH}"
        msg2 = "   Please update MODEL_PATH in the script"
        print(msg1)
        print(msg2)
        log_to_file(msg1)
        log_to_file(msg2)
        exit(1)

    msg = f"Testing GCP detection on: {IMAGE_PATH}"
    print(msg)
    log_to_file(msg)

    time.sleep(5)

# # if __name__ == "__main__":
#     # Check files exist

# while True:
#     if not Path(IMAGE_PATH).exists():
#         print(f"❌ Image file not found: {IMAGE_PATH}")
#         print("   Please update IMAGE_PATH in the script")
#         exit(1)

#     if not Path(MODEL_PATH).exists():
#         print(f"❌ Model file not found: {MODEL_PATH}")
#         print("   Please update MODEL_PATH in the script")
#         exit(1)

#     print(f"Testing GCP detection on: {IMAGE_PATH}")

#     # Run test
#     test_gcp_detection(IMAGE_PATH, MODEL_PATH)
#     time.sleep(5)