import os
import time
import re
from picamera2 import Picamera2

class SimplePiCam:
    def __init__(self, output_dir="OutputImages"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.image_number = self._get_next_image_number()

        self.picam2 = Picamera2()
        config = self.picam2.create_still_configuration(main={"size": (1920, 1080)})
        self.picam2.configure(config)
        self.picam2.start()

    def _get_next_image_number(self):
        files = os.listdir(self.output_dir)
        image_numbers = []

        for f in files:
            match = re.match(r"output(\d{4})\.png", f)
            if match:
                image_numbers.append(int(match.group(1)))

        if image_numbers:
            return max(image_numbers) + 1
        else:
            return 0

    def capture_image(self):
        filename = f"output{self.image_number:04d}.png"
        full_path = os.path.join(self.output_dir, filename)
        self.picam2.capture_file(full_path)
        print(f"Image saved as {full_path}")
        self.image_number += 1

# --- Run forever, every 5 seconds ---
if __name__ == "__main__":
    cam = SimplePiCam()
    while True:
        cam.capture_image()
        time.sleep(5)
