from flask import Flask, Response, render_template_string
from picamera2 import Picamera2
import cv2
import time

app = Flask(__name__)
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.start()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Raspberry Pi Stream</title>
</head>
<body style="text-align: center; background-color: #111; color: #eee;">
    <h1>📷 Live Stream from Pi</h1>
    <img src="/video_feed" style="border: 6px solid #eee;">
</body>
</html>
"""

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
    return render_template_string(HTML)

@app.route('/video_feed')
def video_feed():
    return Response(generate_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
