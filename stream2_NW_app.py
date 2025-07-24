from flask import Flask, Response, render_template_string, request, redirect
from picamera2 import Picamera2
import cv2
import os
import time
from datetime import datetime
from picamera2.encoders import H264Encoder


app = Flask(__name__)
picam2 = Picamera2()

picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.start()

# Output folder
output_folder = "CapturedImages"
os.makedirs(output_folder, exist_ok=True)

# Global video recording state
recording = False
video_filename = ""

# HTML with control buttons
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Raspberry Pi Stream</title>
</head>
<body style="text-align: center; background-color: #111; color: #eee;">
    <h1>📷 Live Stream from Pi</h1>
    <img src="/video_feed" style="border: 6px solid #eee;"><br><br>
    
    <form action="/capture" method="post" style="display: inline-block;">
        <button type="submit" style="padding: 10px 20px; font-size: 16px;">📸 Capture Frame</button>
    </form>

    <form action="/record" method="post" style="display: inline-block; margin-left: 20px;">
        <button type="submit" style="padding: 10px 20px; font-size: 16px;">
            {% if recording %}
            ⏹️ Stop Recording
            {% else %}
            🎥 Start Recording
            {% endif %}
        </button>
    </form>
</body>
</html>
"""

# MJPEG stream
def generate_stream():
    while True:
        frame = picam2.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
        time.sleep(0.1)

@app.route('/')
def index():
    return render_template_string(HTML, recording=recording)

@app.route('/video_feed')
def video_feed():
    return Response(generate_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    frame = picam2.capture_array()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{output_folder}/stream_frame_{timestamp}.png"
    cv2.imwrite(filename, frame)
    print(f"[✔] Frame saved: {filename}")
    return redirect("/")



@app.route('/record', methods=['POST'])
def record():
    global recording, video_filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if not recording:
        video_filename = f"{output_folder}/stream_video_{timestamp}.h264"
        encoder = H264Encoder(bitrate=2000000)
        picam2.start_recording(encoder, video_filename)
        print(f"[🎥] Started recording: {video_filename}")
        recording = True
    else:
        picam2.stop_recording()
        print(f"[⏹️] Stopped recording: {video_filename}")
        recording = False
    return redirect("/")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
