from PIL import Image
import numpy as np
from math import ceil

class AgProjectGCPDetector:
    def __init__(self, input_image_path):
        self.image_path = input_image_path
        self.original_image = Image.open(self.image_path).convert("RGB")
        self.filtered_image = None
        self.corners = {}
        self.midpoints = {}
        self.center = None

    def filter_white_pixels(self, min_val=240, max_val=255):
        img_np = np.array(self.original_image)

        # Create binary mask for white-ish pixels
        mask = (
            (img_np[:, :, 0] >= min_val) & (img_np[:, :, 0] <= max_val) &
            (img_np[:, :, 1] >= min_val) & (img_np[:, :, 1] <= max_val) &
            (img_np[:, :, 2] >= min_val) & (img_np[:, :, 2] <= max_val)
        )

        filtered_img_np = np.zeros_like(img_np)
        filtered_img_np[mask] = [255, 255, 255]
        self.filtered_image = Image.fromarray(filtered_img_np)

        return mask, filtered_img_np

    def save_filtered_image(self, output_path="GCPOF_filtered.png"):
        if self.filtered_image:
            self.filtered_image.save(output_path)

    def find_center(self):
        if self.filtered_image is None:
            raise RuntimeError("Run filter_white_pixels() before detecting center.")

        img_np = np.array(self.filtered_image)
        white_mask = np.all(img_np == [255, 255, 255], axis=2)
        ys, xs = np.where(white_mask)

        if len(xs) == 0 or len(ys) == 0:
            print("No white pixels found.")
            return None

        x_min, x_max = int(xs.min()), int(xs.max())
        y_min, y_max = int(ys.min()), int(ys.max())

        # Corners
        self.corners = {
            "top_left": (x_min, y_min),
            "top_right": (x_max, y_min),
            "bottom_right": (x_max, y_max),
            "bottom_left": (x_min, y_max),
        }

        # Midpoints of diagonals
        mid1 = (ceil((x_min + x_max) / 2), ceil((y_min + y_max) / 2))  # TL to BR
        mid2 = (ceil((x_max + x_min) / 2), ceil((y_min + y_max) / 2))  # TR to BL
        self.midpoints = {"diag1": mid1, "diag2": mid2}

        # Final averaged center
        self.center = ((mid1[0] + mid2[0]) / 2, (mid1[1] + mid2[1]) / 2)
        return self.center

    def print_summary(self):
        if not self.center:
            print("Center not computed.")
            return

        print("Corners of the white region:")
        for name, coord in self.corners.items():
            print(f"{name.replace('_', ' ').title()}: {coord}")

        print("\nMidpoints of diagonals:")
        for name, coord in self.midpoints.items():
            print(f"{name.title()}: {coord}")

        print(f"\nAveraged center point: {self.center}")

# === Example usage ===
if __name__ == "__main__":
    detector = AgProjectGCPDetector("AP_getCam.png")
    detector.filter_white_pixels()
    detector.save_filtered_image("AP_model_output.png")
    detector.find_center()
    detector.print_summary()
