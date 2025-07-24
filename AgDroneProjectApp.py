from flask import Flask, render_template, request, redirect, url_for
from threading import Thread, Event
import time
import os

from AP_getCam import AgProjectGCPPlacer
from AP_model import AgProjectGCPDetector

app = Flask(__name__)
os.makedirs("static", exist_ok=True)

output_info = {}
running_event = Event()
worker_thread = None

import shutil

def gcp_loop():
    while running_event.is_set():
        placer = AgProjectGCPPlacer("BaseGreenField.png", "gcp_singleRing_fixed_pattern.png")
        placer.apply_random_transform()
        placer.place_overlay()
        placer.save_result("static/tmp_AP_getCam.png")  # save to temp

        output_info["scale"] = round(placer.scale_factor, 4)
        output_info["angle"] = round(placer.angle, 2)
        output_info["position"] = placer.center_position

        detector = AgProjectGCPDetector("static/tmp_AP_getCam.png")
        detector.filter_white_pixels()
        detector.save_filtered_image("static/tmp_AP_model_output.png")  # save to temp
        output_info["gcp_center"] = detector.find_center()

        # Atomically replace both images
        shutil.move("static/tmp_AP_getCam.png", "static/AP_getCam.png")
        shutil.move("static/tmp_AP_model_output.png", "static/AP_model_output.png")

        time.sleep(5)


@app.route("/", methods=["GET", "POST"])
def index():
    global worker_threadpyth

    if request.method == "POST":
        action = request.form.get("action")

        if action == "start" and not running_event.is_set():
            running_event.set()
            worker_thread = Thread(target=gcp_loop)
            worker_thread.start()

        elif action == "stop":
            running_event.clear()
            if worker_thread:
                worker_thread.join(timeout=1)

        return redirect(url_for("index"))

    return render_template("index.html", info=output_info, running=running_event.is_set())

if __name__ == "__main__":
    app.run(debug=True)
