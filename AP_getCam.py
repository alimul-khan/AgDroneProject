from PIL import Image
import random

class AgProjectGCPPlacer:
    def __init__(self, base_image_path, overlay_image_path):
        self.base_path = base_image_path
        self.overlay_path = overlay_image_path
        self.base_image = Image.open(self.base_path).convert("RGBA")
        self.overlay_image = Image.open(self.overlay_path).convert("RGBA")
        self.scale_factor = None
        self.angle = None
        self.center_position = None

    def apply_random_transform(self, min_scale=0.05, max_scale=0.12):
        # Random rotation
        self.angle = random.uniform(0, 360)
        rotated_overlay = self.overlay_image.rotate(self.angle, expand=True)

        # Random scale based on base image
        self.scale_factor = random.uniform(min_scale, max_scale)
        new_width = int(self.base_image.width * self.scale_factor)
        aspect_ratio = rotated_overlay.height / rotated_overlay.width
        new_height = int(new_width * aspect_ratio)
        self.overlay_image = rotated_overlay.resize((new_width, new_height), Image.LANCZOS)

    def place_overlay(self, center_x=None, center_y=None):
        if center_x is None:
            center_x = random.randint(0, self.base_image.width - self.overlay_image.width)
        if center_y is None:
            center_y = random.randint(0, self.base_image.height - self.overlay_image.height)

        self.center_position = (center_x, center_y)

        # Top-left corner to paste
        x = center_x - self.overlay_image.width // 2
        y = center_y - self.overlay_image.height // 2

        self.base_image.paste(self.overlay_image, (x, y), self.overlay_image)

    def save_result(self, output_path="AP_getCam.png"):
        self.base_image.convert("RGB").save(output_path)
        print(f"Scale factor: {self.scale_factor:.4f}, Rotation angle: {self.angle:.2f}, Center Position: {self.center_position}")

# === Example usage ===
if __name__ == "__main__":
    placer = AgProjectGCPPlacer("BaseGreenField.png", "gcp_singleRing_fixed_pattern.png")
    placer.apply_random_transform()
    placer.place_overlay()  # Optional: pass center_x, center_y
    placer.save_result("AP_getCam.png")
