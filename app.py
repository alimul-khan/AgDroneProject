from flask import Flask, render_template, send_from_directory
from image_generator import RandomColorImage
import os
import threading
import time

app = Flask(__name__)
latest_info = {
    "color": (0, 0, 0),
    "timestamp": ""
}

def image_updater():
    while True:
        img = RandomColorImage()
        img.create_image()
        img.save()
        latest_info["color"] = img.color
        latest_info["timestamp"] = img.timestamp
        time.sleep(5)

@app.route('/')
def index():
    return render_template("index.html",
                           rgb=latest_info["color"],
                           timestamp=latest_info["timestamp"])

@app.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory('static', filename)

if __name__ == "__main__":
    threading.Thread(target=image_updater, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
