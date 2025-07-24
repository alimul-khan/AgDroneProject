from PIL import Image

# Load the image
image_path = "output_22-Jul-2025-23:26:53.png"  # Replace with your image file
img = Image.open(image_path)

# Get pixel size
width, height = img.size
print(f"Image size: {width} x {height} pixels")
