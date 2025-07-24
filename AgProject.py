from AP_getCam import AgProjectGCPPlacer

# Create an instance
placer = AgProjectGCPPlacer("BaseGreenField.png", "gcp_singleRing_fixed_pattern.png")

# Apply random scale and rotation
placer.apply_random_transform()

# Place GCP at random or fixed location (optional to pass coordinates)
placer.place_overlay()
# placer.place_overlay(center_x=20, center_y=400)

# Save result
placer.save_result("AP_getCam.png")


from AP_model import AgProjectGCPDetector

detector = AgProjectGCPDetector("AP_getCam.png")
detector.filter_white_pixels()
detector.save_filtered_image("AP_model_output.png")
center = detector.find_center()
print("GCP Center:", center)
