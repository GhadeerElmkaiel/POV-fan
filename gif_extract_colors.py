import numpy as np
from PIL import Image
import math
from pathlib import Path
import os

NUM_SLICES = 100
NUM_LEDS = 72

# Function to extract color indices from the circular region based on slices and LED spots
def extract_colors_by_slices(image, radius, num_slices=NUM_SLICES, num_leds=NUM_LEDS):
    width, height = image.size
    center_x, center_y = width // 2, height // 2
    
    # Create a 2D array (list of lists) to store the color indices for each LED spot in each slice
    image_colors = []
	
	
    # Calculate the angle increment per slice
    angle_increment = 360 / num_slices
    
    # Iterate over each slice (defined by angles)
    for slice_idx in range(num_slices):
        slice_colors = []
        # Calculate the middle angle for the current slice
        angle_deg = slice_idx * angle_increment
        angle_rad = math.radians(angle_deg)

        # Iterate over each LED spot within the slice (defined by radial distance)
        for led_idx in range(num_leds):
            # Calculate the radial distance for this LED spot
            radial_distance = (led_idx + 1) * (radius / num_leds)

            # Convert polar coordinates (angle, radius) to Cartesian coordinates (x, y)
            x = int(center_x + radial_distance * math.cos(angle_rad))
            y = int(center_y + radial_distance * math.sin(angle_rad))

            # Make sure we're within the image bounds
            if 0 <= x < width and 0 <= y < height:
                pixel_color = image.getpixel((x, y))
                slice_colors.append(pixel_color)
                
        image_colors.append(slice_colors)

    return image_colors

# Load 

gif_name = "earth"
sequence_path = f"gif_sequences/{gif_name}/"

files = os.listdir(sequence_path)

print(files)

folder_path = "gif_colors/" + gif_name
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

for image_name in files:
    image_path = f"gif_sequences/{gif_name}/{image_name}"
    image = Image.open(image_path)
    
    path = Path(image_path)
    image_name_no_extension = path.stem

    # Convert image to RGB if it's not already in RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Extract circular region
    radius = min(image.size) // 2 - 1  # Assume the radius to be half of the smaller dimension

    # Extract color palette and indices from the circular region
    image_colors = extract_colors_by_slices(image, radius)

    image_colors = np.array(image_colors)

    # Save the color indices array as a numpy file
    np.save('gif_colors/{}/{}.npy'.format(gif_name, image_name_no_extension), image_colors)


