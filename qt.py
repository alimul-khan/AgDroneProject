import time
from picamera2 import Picamera2

class SimplePiCam:
    def __init__(self, filename="test.png"):
        self.filename = filename
        self.picam2 = Picamera2()
        config = self.picam2.create_still_configuration(main={"size": (1920, 1080)})
        self.picam2.configure(config)
        self.picam2.start()

    def capture_image(self):
        self.picam2.capture_file(self.filename)
        print(f"Image saved as {self.filename}")

# --- Run forever, every 5 seconds ---
cam = SimplePiCam()

while True:
    cam.capture_image()
    time.sleep(5)
