import os
import time
import re
import tempfile
from datetime import datetime
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image
from ultralytics import YOLO

# =============================================================================
# CONFIGURATION
# =============================================================================
OUTPUT_DIR = "OutputImages"
MODEL_PATH = "best.pt"
CAPTURE_INTERVAL = 1  # seconds between shots (post-processing settle)
LOG_DIR = "LogFiles"

# =============================================================================
# Helpers (filesystem + logging)
# =============================================================================
os.makedirs(LOG_DIR, exist_ok=True)
timestamp_str = datetime.now().strftime("%d-%b-%y_%H_%M_%S")
LOG_FILE = f"{LOG_DIR}/Log_{timestamp_str}.txt"

def append_log(message: str):
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_latest_image_number():
    """Find highest output####.JPG number in OUTPUT_DIR."""
    files = os.listdir(OUTPUT_DIR)
    numbers = []
    for f in files:
        m = re.match(r"output(\d{4})\.(jpg|jpeg|JPG|JPEG)$", f)
        if m:
            numbers.append(int(m.group(1)))
    return max(numbers) if numbers else 0

# =============================================================================
# Image loading for YOLO (kept from your pipeline)
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
# gphoto2 camera control (Canon USB)
# =============================================================================
def run_cmd(args):
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def prime_camera():
    # Avoid desktop auto-mounter grabbing the camera; harmless if not running
    run_cmd(["killall", "gvfs-gphoto2-volume-monitor"])
    run_cmd(["killall", "gvfsd-gphoto2"])
    # Save to SD card (more reliable)
    run_cmd(["gphoto2", "--set-config", "capturetarget=1"])
    # (Optional) If you still see “reviewtime 2s” in logs, you can force it off:
    # run_cmd(["gphoto2", "--set-config", "reviewtime=0"])

def capture_one_jpeg(output_path, wait_s=8):
    """
    Trigger shutter, wait for camera to report the new object, download to output_path.
    Returns (ok: bool, info: str)
    """
    r1 = run_cmd(["gphoto2", "--trigger-capture"])
    if r1.returncode != 0:
        return False, f"trigger failed: {r1.stderr.strip()}"

    r2 = run_cmd([
        "gphoto2",
        f"--wait-event-and-download={wait_s}s",
        f"--filename={output_path}",
        "--force-overwrite"
    ])
    if r2.returncode != 0:
        return False, r2.stderr.strip()
    return True, r2.stdout.strip()

# =============================================================================
# Main Loop
# =============================================================================
def main():
    ensure_output_dir()

    if not Path(MODEL_PATH).exists():
        print(f"Model not found: {MODEL_PATH}")
        return

    model = YOLO(MODEL_PATH)
    prime_camera()

    image_counter = get_latest_image_number() + 1

    print("📸 Canon capture started. Press Ctrl+C to stop.")
    append_log("=== Canon USB capture session started ===")

    try:
        while True:
            filename = f"output{image_counter:04d}.JPG"
            image_path = os.path.join(OUTPUT_DIR, filename)

            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = f"[{ts}] Capturing: {image_path}"
            print(msg); append_log(msg)

            ok, info = capture_one_jpeg(image_path, wait_s=8)
            if not ok:
                if "PTP Device Busy" in info or "I/O in progress" in info:
                    print("⚠️ Camera busy; waiting 4s and retrying…")
                    append_log("Busy; retrying after 4s")
                    time.sleep(4)
                    ok2, info2 = capture_one_jpeg(image_path, wait_s=10)
                    if not ok2:
                        err = f"Capture failed after retry: {info2}"
                        print("❌ " + err); append_log("ERROR " + err)
                        break
                else:
                    err = f"Capture failed: {info}"
                    print("❌ " + err); append_log("ERROR " + err)
                    break

            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = f"[{ts}] Captured: {image_path}"
            print(msg); append_log(msg)

            # Run your detector
            test_gcp_detection(image_path, model)

            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = f"[{ts}] Processed: {image_path}"
            print(msg); append_log(msg)

            print("-" * 40); append_log("-" * 40); append_log("")

            image_counter += 1
            time.sleep(CAPTURE_INTERVAL)  # small settle delay for next loop

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
        append_log("=== Session stopped by user ===")

if __name__ == "__main__":
    main()
