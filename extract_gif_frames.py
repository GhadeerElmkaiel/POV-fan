import os
from PIL import Image

# Function to extract frames from a GIF and save them as individual PNG files
def extract_frames_from_gif(gif_path, num_frames):
	base_name = os.path.basename(gif_path)
	folder_name = os.path.splitext(base_name)[0] 
	
	folder_path = "gif_sequences/" + folder_name
	if not os.path.exists(folder_path):
		os.makedirs(folder_path)
	
	# Open the GIF file	
	gif = Image.open(gif_path)
	
	total_frames = gif.n_frames
	multiplier = total_frames/num_frames
	
	for frame in range(num_frames):
		frame_iter = int(frame*multiplier)
		frame_iter = min(frame_iter, total_frames-1)
		gif.seek(frame_iter)
		frame_image = gif.copy() # Copy the frame from the gif
		
		frame_file_path = os.path.join(folder_path, f"frame_{frame}.png")
		
		frame_image.save(frame_file_path)
		
	print(f"Extracted {num_frames} frames into folder: '{folder_name}'")
	

# number of frames to extract from the GIF
num_frames = 20
gif_name = "earth"
gif_path = "gifs/{}.gif".format(gif_name)
extract_frames_from_gif(gif_path, num_frames)
