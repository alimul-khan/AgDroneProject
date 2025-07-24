from picamera2 import Picamera2

class SimplePiCam:
    def __init__(self, filename="rPiCameraImage.png"):
        self.filename = filename
        self.picam2 = Picamera2()

    def capture_image(self):
        config = self.picam2.create_still_configuration(main={"size": (1920, 1080)})
        self.picam2.configure(config)
        self.picam2.start()
        self.picam2.capture_file(self.filename)
        print(f"Image saved as {self.filename}")

if __name__ == "__main__":
    cam = SimplePiCam()
    cam.capture_image()




# from picamera2 import Picamera2
# from datetime import datetime
# import os

# # Create output folder
# output_folder = "OutputImages"
# os.makedirs(output_folder, exist_ok=True)

# # Generate timestamp
# timestamp = datetime.now().strftime("%d-%b-%Y-%H:%M:%S")
# filename = f"{output_folder}/output_{timestamp}.png"

# # Initialize and configure the camera
# picam2 = Picamera2()
# config = picam2.create_still_configuration(main={"size": (1920, 1080)})
# picam2.configure(config)
# picam2.start()

# # Capture and save the image
# picam2.capture_file(filename)

# print(f"Image saved as {filename}")
