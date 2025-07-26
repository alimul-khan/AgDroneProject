import os
import time
import json
import threading
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, send_from_directory, jsonify
from picamera2 import Picamera2
import imageio
import numpy as np

app = Flask(__name__)

output_folder = "AgLabImages"
os.makedirs(output_folder, exist_ok=True)

initial_timestamp = datetime.now().strftime("%d-%b-%y-%H-%M-%S")
stats_output_file = f"AgLabImageStats_{initial_timestamp}.json"
with open(stats_output_file, "w") as f:
    json.dump([], f)

capturing = False
capture_thread = None
latest_image = None
latest_info = None
processor = None

class ImageCaptureProcessor:
    def __init__(self):
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_still_configuration(main={"size": (1920, 1080)}))
        self.picam2.start()

    def capture_and_process(self):
        global latest_image, latest_info, capturing
        while capturing:
            ts = datetime.now().strftime("%d-%b-%y-%H-%M-%S")
            filename = f"agLab_{ts}.png"
            filepath = os.path.join(output_folder, filename)
            self.picam2.capture_file(filepath)
            print(f"[✓] Captured {filename}")

            stats = self.get_image_stats(filepath)
            latest_image = filename
            latest_info = stats

            with open(stats_output_file, "r+") as f:
                data = json.load(f)
                data.append(stats)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()

            time.sleep(5)

    def get_image_stats(self, image_path):
        image = imageio.imread(image_path)
        height, width = image.shape[:2]
        num_channels = 1 if image.ndim == 2 else image.shape[2]
        channel_stats = {}

        if num_channels == 1:
            channel_stats["0"] = self._stats_for_channel(image)
        else:
            for i in range(num_channels):
                channel = image[:, :, i]
                channel_stats[str(i)] = self._stats_for_channel(channel)

        stats = {
            "image_name": os.path.basename(image_path),
            "dimensions": f"{height} x {width}",
            "num_channels": num_channels
        }

        for ch, vals in channel_stats.items():
            stats[f"channel_{ch}_min"] = vals["min"]
            stats[f"channel_{ch}_max"] = vals["max"]
            stats[f"channel_{ch}_mean"] = vals["mean"]

        return stats

    def _stats_for_channel(self, data):
        return {
            "min": int(np.min(data)),
            "max": int(np.max(data)),
            "mean": round(float(np.mean(data)), 2)
        }

    def close(self):
        self.picam2.close()

@app.route("/")
def index():
    with open(stats_output_file, "r") as f:
        data = json.load(f)
    return render_template("index.html", capturing=capturing, latest_image=latest_image, latest_info=latest_info, all_stats=data)

@app.route("/toggle")
def toggle_capture():
    global capturing, capture_thread, processor
    if not capturing:
        capturing = True
        processor = ImageCaptureProcessor()
        capture_thread = threading.Thread(target=processor.capture_and_process)
        capture_thread.start()
    else:
        capturing = False
        if processor:
            processor.close()
    return redirect(url_for('index'))

@app.route("/latest")
def latest():
    return jsonify({
        "image": latest_image,
        "info": latest_info
    })

@app.route("/stats")
def stats():
    with open(stats_output_file, "r") as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/images/<filename>')
def send_image(filename):
    return send_from_directory(output_folder, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
