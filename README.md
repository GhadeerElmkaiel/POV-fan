# POV Fan Project

## 🔗 YouTube Videos

### ▶️ English version  
[![Watch the video](https://img.youtube.com/vi/GS9G-EpY_SY/hqdefault.jpg)](https://youtu.be/GS9G-EpY_SY?si=elMvtA2VpS_cLbiC)

### ▶️ Arabic version  
[![Watch the video](https://img.youtube.com/vi/qHcmiEZY0y4/hqdefault.jpg)](https://youtu.be/qHcmiEZY0y4?si=-6HQ0VZoEA3KTZWj)

This repository contains code for a Persistence of Vision (POV) fan display using addressable LEDs and image processing in Python. The project allows you to convert images into color data for a rotating LED fan and display static or animated images.

## Features
- Convert images to LED color data for POV display
- Supports static images and GIFs
- Optimized real-time LED control for Raspberry Pi

## Folder Structure
- `optimized_pov_fan.py`: Main script for running the POV fan on Raspberry Pi
- `sequence_pov_fan_optimized.py`: Script for running the POV fan to show a squence of frames
- `Img_colors.py`: Script to process images and extract color data for the fan using one half of the fan
- `Img_douple_resolution_colors.py`: Script to process images and extract color data for the double resolution fan as explained in the video
- `extract_gif_frames.py`: Script to process gifs and extract frames to show
- `Img_colors.py`: Script to process the gif frames and extract color data for each frame
- `colors/`: Contains generated color data (`.npy` files) for images
- `gif_colors/`, `gif_sequences/`, `gifs/`, `images/`: Example images and processed frames

## Image Processing
To convert an image for POV display:
1. Place your image in the `images/` folder (e.g., `images/Smiley_face.png`).
2. Run the image processing script:
	```bash
	python Img_colors.py
	```
    or
	```bash
	python Img_douple_resolution_colors.py
	```
	This will generate a color data file in `colors/half_line/` (e.g., `Smiley_face.npy`), or in `colors/double_resolution/` (e.g., `douple_res_Smiley_face.npy`)

## Running the POV Fan
1. Ensure the color data file exists in the appropriate folder (e.g., `colors/douple_resolution/douple_res_Smiley_face.npy`).
2. Edit `optimized_pov_fan.py` to set `image_name` to your image (without extension).
3. Run the main script on your Raspberry Pi:
	```bash
	python optimized_pov_fan.py
	```

## Notes
- The number of LEDs and slices can be configured in the scripts.
- For GIFs or animations, use the provided scripts to extract frames and generate color data.
- Make sure to run the scripts on a Raspberry Pi with the required hardware connected.

## License
MIT License
