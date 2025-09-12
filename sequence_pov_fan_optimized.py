import time
from rpi_ws281x import PixelStrip, Color
import numpy as np
import RPi.GPIO as GPIO
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import threading
import os

# Configuration

NUM_LEDS_TOTAL = 72
# Use either 72 for douple resolution or 36 for single resolution
NUM_LEDS_TO_ACTIVATE = 72 # The number of the LEDs to activate in the fan (the rest will be off)
NUM_LEDS_TO_USE = 72 # The number of the LEDs to use in the fan (the rest will be off) 
# NUM_LEDS_TO_ACTIVATE = 36 # The number of the LEDs to activate in the fan (the rest will be off)
# NUM_LEDS_TO_USE = 36 # The number of the LEDs to use in the fan (the rest will be off)

BRIGHTNESS_RATIO = 0.2
NUM_DIVS = 100  # Number of divisions (lines) in one full rotation
palette_size = 10
if NUM_LEDS_TO_ACTIVATE == 36:
    LINES_TO_SHIFT = -24 # This is to align the image properly. Adjust as needed.
else:
    LINES_TO_SHIFT = -18


LED_PIN = 18          # GPIO pin connected to the data line (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800kHz).
LED_DMA = 10          # DMA channel to use for generating signal.
LED_BRIGHTNESS = 50  # Brightness of the LED (0-255).
LED_INVERT = False    # True to invert the signal (for level shifter).
LED_CHANNEL = 0       # Set to 1 for GPIOs 13, 19, 41, 45, 53.


not_received_color = Color(2, 1, 5)
first_line_colors = [Color(5, 5, 0)] * NUM_LEDS_TO_USE
line_to_show_colors = first_line_colors.copy()
line_iter = 0

# POV clock variables
previous_micros = 0
counter_1 = 0
current_count = 0
line_start_time = 0
line_end_time = 0

# Interruption variables to count rotation speed
last_IN_state = 0
one_rot_time = 0
time_per_deg = 0
degs_per_line = 360.0 / NUM_DIVS  # Using 50 divisions


# Timer and delay settings
delay_time_micro = 2000000
line_end = False
num_ms_delay = 20
rotation_end = False
rot_per_frame = 4 # Number of rotations per frame, to display videos or animations


rotation_end_event = threading.Event()
rot_number = 0


# Define the GPIO pin where the interrupt is connected
INTERRUPT_PIN = 4

# Set up the GPIO
GPIO.setmode(GPIO.BCM)
#GPIO.setup(INTERRUPT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(INTERRUPT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Initialize LED strip
strip = PixelStrip(NUM_LEDS_TO_ACTIVATE, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

sequence_name = "earth" # Name of the sequence (folder in gif_colors)
path_to_sequence = f"gif_colors/{sequence_name}/"

# Get all frames of the sequence
files = os.listdir(path_to_sequence)

files = sorted(files)
num_frames = len(files)

sequence_colors = np.array([])



num_leds_one_side = NUM_LEDS_TOTAL//2

# Load all frames colors into sequence_colors
for num, image_name in enumerate(files):
    colors_array = []
    image_path = f"gif_colors/{sequence_name}/{image_name}"
    slices_colors = np.load(image_path) 
    slices_colors = slices_colors.tolist()

    for line in range(NUM_DIVS):
        line_array = [Color(0,0,0) for _ in range(NUM_LEDS_TOTAL)]
            
        for i in range(num_leds_one_side):
            color_arr = slices_colors[line][i*2+1]
            corrected_brightness = BRIGHTNESS_RATIO/((num_leds_one_side-i)/10.0)
            corrected_brightness = BRIGHTNESS_RATIO
            color = Color(int(color_arr[1]*corrected_brightness), int(color_arr[0]*corrected_brightness), int(color_arr[2]*corrected_brightness))
            line_array[num_leds_one_side - i - 1] = color
        for i in range(num_leds_one_side):
            corrected_brightness = BRIGHTNESS_RATIO/((num_leds_one_side-i)/10.0)
            corrected_brightness = BRIGHTNESS_RATIO
            color_arr = slices_colors[(line+NUM_DIVS//2)%NUM_DIVS][i*2]
            color = Color(int(color_arr[1]*corrected_brightness), int(color_arr[0]*corrected_brightness), int(color_arr[2]*corrected_brightness))
            line_array[num_leds_one_side+i] = color
        colors_array.append(line_array)
    if num == 0:
        sequence_colors = [colors_array]
    else:
        sequence_colors.append(colors_array)
        


frame_iter = 0    
frame_colors = sequence_colors[frame_iter]


# Precise delay function
def precise_micros_delay(micros_to_delay):
    start = time.perf_counter()*1000000
    end = time.perf_counter()*1000000
    while (end-start)<micros_to_delay and not rotation_end_event.is_set():
        end = time.perf_counter()*1000000
        

def handle_interrupt_rising(channel):
    global counter_1, current_count, one_rot_time, time_per_deg, previous_micros, line_iter, delay_time_micro, rot_number, frame_iter
    current_count = time.time() * 1_000_000  # Get current time in microseconds
    
    rotation_end_event.set()
    line_iter = 0
    
    one_rot_time = current_count - counter_1
    time_per_deg = one_rot_time / 360.0
    delay_time_micro = time_per_deg*degs_per_line
    previous_micros = time.time() * 1_000_000
    # print("Line number {}".format(rot_number))
    rot_number = rot_number+1
    
    # Update frame
    if rot_number%rot_per_frame == 0:
        frame_iter = (frame_iter+1)%num_frames
    
            
    counter_1 = current_count


GPIO.add_event_detect(INTERRUPT_PIN, GPIO.RISING, callback=handle_interrupt_rising)
    
    
def LEDsLineTimerOptimized(line_num):
    line_iter_to_show = (line_num + LINES_TO_SHIFT + 2*NUM_DIVS)%NUM_DIVS
    global line_end_time, line_start_time, frame_colors, num_frames, frame_iter
    for i in range(NUM_LEDS_TO_USE):
        color = sequence_colors[frame_iter][line_iter_to_show][i]
        # print(color)
        strip.setPixelColor(i, color)

    # Show the LEDs
    strip.show()

    line_end_time = time.perf_counter()
    difference = (line_end_time - line_start_time)*1000000
    time_to_wait = delay_time_micro - difference
    if time_to_wait > 0:
        precise_micros_delay(time_to_wait)
    line_start_time = time.perf_counter()
    

def main():
    global line_to_show_colors, line_iter, rotation_end

    try:
        line_iter = 0
        while True:
            if rotation_end_event.is_set():
                rotation_end_event.clear()
                line_iter = 0
            
            LEDsLineTimerOptimized(line_iter)  # Call function to show the line
            line_iter = (line_iter + 1)%NUM_DIVS
            
                
    except KeyboardInterrupt:
        print("Exiting...")
        color = Color(0, 0, 0)
        for i in range(NUM_LEDS_TO_USE):
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(5.0/1000.0)
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
