from flask import Flask, Response, render_template_string, request, redirect
from picamera2 import Picamera2
import cv2
import time
import os
from datetime import datetime

app = Flask(__name__)

# Initialize camera
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.start()

# Output folder
os.makedirs("CapturedImages", exist_ok=True)

# HTML with capture button
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Raspberry Pi Stream</title>
</head>
<body style="text-align: center; background-color: #111; color: #eee;">
    <h1>📷 Live Stream from Pi</h1>
    <img src="/video_feed" style="border: 6px solid #eee;"><br><br>
    <form action="/capture" method="post">
        <button type="submit" style="padding: 10px 20px; font-size: 18px;">📸 Capture Frame</button>
    </form>
</body>
</html>
"""

# MJPEG stream generator
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

# Routes
@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/video_feed')
def video_feed():
    return Response(generate_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    frame = picam2.capture_array()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"CapturedImages/stream_{timestamp}.png"
    cv2.imwrite(filename, frame)
    print(f"Saved: {filename}")
    return redirect("/")

# Start server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
