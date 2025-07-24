from PIL import Image
import random
from datetime import datetime

class RandomColorImage:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.color = self.generate_random_color()
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.image = None

    def generate_random_color(self):
        return tuple(random.randint(0, 255) for _ in range(3))

    def create_image(self):
        self.image = Image.new("RGB", (self.width, self.height), self.color)

    def save(self, filename="static/output.png"):
        if self.image is None:
            self.create_image()
        self.image.save(filename)
