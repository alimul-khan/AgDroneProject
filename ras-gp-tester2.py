import tempfile
from pathlib import Path
import numpy as np
from PIL import Image
from ultralytics import YOLO
import time
import sys

# =============================================================================
# CONFIGURATION
# =============================================================================
IMAGE_PATH = "test.png"
MODEL_PATH = "best.pt"
LOG_FILE = "test.txt"

# =============================================================================
# Tee print() to both terminal and file (with flush)
# =============================================================================
class TeeOutput:
    def __init__(self, file_path):
        self.terminal = sys.__stdout__
        self.log = open(file_path, "a", buffering=1)  # Line-buffered (important)

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = TeeOutput(LOG_FILE)

# =============================================================================
# Image and detection functions
# =============================================================================

def load_image(image_path, channel=2):
    arr = np.array(Image.open(image_path))
    if arr.ndim == 3 and arr.shape[2] > channel:
        channel_data = arr[:, :, channel]
    elif arr.ndim == 2:
        channel_data = arr
    else:
        channel_data = arr[:, :, -1] if arr.ndim == 3 else arr

    if channel_data.dtype != np.uint8:
        channel_data = ((channel_data - channel_data.min()) /
                        (channel_data.max() - channel_data.min()) * 255).astype(np.uint8)

    return np.stack([channel_data] * 3, axis=2)

def test_gcp_detection(image_path, model_path, channel=2):
    model = YOLO(model_path)
    image = load_image(image_path, channel)

    temp_path = tempfile.mktemp(suffix='.jpg')
    Image.fromarray(image).save(temp_path, 'JPEG', quality=95)

    try:
        for conf in [0.25, 0.1, 0.05, 0.01]:
            results = model(temp_path, conf=conf, verbose=False)
            detections = results[0].boxes

            if detections is not None and len(detections) > 0:
                print(f"✅ GCP DETECTED: Found {len(detections)} GCP(s) with confidence ≥ {conf}")
                return True

        print("❌ NO GCP DETECTED")
        return False

    finally:
        try:
            Path(temp_path).unlink()
        except:
            pass

# =============================================================================
# Main loop
# =============================================================================

while True:
    if not Path(IMAGE_PATH).exists():
        print(f"❌ Image file not found: {IMAGE_PATH}")
        print("   Please update IMAGE_PATH in the script")
        exit(1)

    if not Path(MODEL_PATH).exists():
        print(f"❌ Model file not found: {MODEL_PATH}")
        print("   Please update MODEL_PATH in the script")
        exit(1)

    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Testing GCP detection on: {IMAGE_PATH}")
    test_gcp_detection(IMAGE_PATH, MODEL_PATH)

    time.sleep(5)
