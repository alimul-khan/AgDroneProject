import os
import time
import re
import tempfile
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image
from ultralytics import YOLO
from picamera2 import Picamera2


# =============================================================================
# CONFIGURATION
# =============================================================================
from datetime import datetime

OUTPUT_DIR = "OutputImages"
MODEL_PATH = "best.pt"

# Ensure LogFiles directory exists and generate timestamped log filename
os.makedirs("LogFiles", exist_ok=True)
timestamp_str = datetime.now().strftime("%d-%b-%y_%H_%M_%S")
LOG_FILE = f"LogFiles/Log_{timestamp_str}.txt"

CAPTURE_INTERVAL = 1  # seconds

# =============================================================================
# Helper Functions
# =============================================================================

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_latest_image_number():
    files = os.listdir(OUTPUT_DIR)
    numbers = []

    for f in files:
        m = re.match(r"output(\d{4})\.png", f)
        if m:
            numbers.append(int(m.group(1)))

    return max(numbers) if numbers else 0

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

def append_log(message):
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

def log_to_file(image_name, detected):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = "Yes" if detected else "No"
    line = f"[{timestamp}] Image: {image_name} | GCP detected: {result}"
    print(line)
    append_log(line)

def test_gcp_detection(image_path, model, channel=2):
    image = load_image(image_path, channel)
    temp_path = tempfile.mktemp(suffix=".jpg")
    Image.fromarray(image).save(temp_path, 'JPEG', quality=95)

    try:
        for conf in [0.25, 0.1, 0.05, 0.01]:
            results = model(temp_path, conf=conf, verbose=False)
            detections = results[0].boxes

            if detections is not None and len(detections) > 0:
                log_to_file(Path(image_path).name, True)
                return True

        log_to_file(Path(image_path).name, False)
        return False

    finally:
        Path(temp_path).unlink(missing_ok=True)

# =============================================================================
# Main Loop
# =============================================================================

def main():
    ensure_output_dir()

    if not Path(MODEL_PATH).exists():
        print(f"Model not found: {MODEL_PATH}")
        return

    model = YOLO(MODEL_PATH)

    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": (1920, 1080)})
    picam2.configure(config)
    picam2.start()
    time.sleep(2)

    image_counter = get_latest_image_number() + 1

    while True:
        filename = f"output{image_counter:04d}.png"
        image_path = os.path.join(OUTPUT_DIR, filename)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] Capturing: {image_path}"
        print(msg)
        append_log(msg)

        picam2.capture_file(image_path)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] Captured: {image_path}"
        print(msg)
        append_log(msg)

        test_gcp_detection(image_path, model)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] Processed: {image_path}"
        print(msg)
        append_log(msg)

        print("-" * 40)
        append_log("-" * 40)
        append_log("")  # blank line

        image_counter += 1
        time.sleep(CAPTURE_INTERVAL)

if __name__ == "__main__":
    main()
