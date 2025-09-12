import time
from rpi_ws281x import PixelStrip, Color
import numpy as np
import RPi.GPIO as GPIO
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import threading
# from led_controller import update_led_strip

# Configuration

NUM_LEDS_TOTAL = 72
NUM_LEDS_TO_ACTIVATE = 72
NUM_LEDS_TO_USE = 72

BRIGHTNESS_RATIO = 0.2
NUM_DIVS = 100
palette_size = 10
LINES_TO_SHIFT = -15


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

image_name = "Smiley_face"

# Load the saved colors matrix
slices_colors = np.load('colors/douple_resolution/douple_res_{}.npy'.format(image_name)) 
# slices_colors = np.load('gif_colors/eyegif/frame_0.npy'.format(image_name)) 
slices_colors = slices_colors.tolist()

colors_array = []
running_colors = [None for i in range(NUM_LEDS_TO_USE)]

# Function to create a precise delay in microseconds
def precise_micros_delay(micros_to_delay):
    start = time.perf_counter_ns()
    end = start
    while (end-start) < micros_to_delay*1000 and not rotation_end_event.is_set():
        end = time.perf_counter_ns()
        

# This function to order the colors in a correct way to be used easily later
def arrange_colors(slices_colors):
    arranged_colors = []
    num_leds_one_side = NUM_LEDS_TOTAL//2 
    for line_iter in range(NUM_DIVS):
        line_array = [Color(0,0,0) for _ in range(NUM_LEDS_TOTAL)]
        for i in range(num_leds_one_side):
            color_arr = slices_colors[line_iter][i*2+1]
            color = Color(int(color_arr[1]*BRIGHTNESS_RATIO), int(color_arr[0]*BRIGHTNESS_RATIO), int(color_arr[2]*BRIGHTNESS_RATIO))
            line_array[num_leds_one_side - i - 1] = color
        for i in range(num_leds_one_side):
            color_arr = slices_colors[(line_iter+NUM_DIVS//2)%NUM_DIVS][i*2]
            color = Color(int(color_arr[1]*BRIGHTNESS_RATIO), int(color_arr[0]*BRIGHTNESS_RATIO), int(color_arr[2]*BRIGHTNESS_RATIO))
            line_array[num_leds_one_side+i] = color
        arranged_colors.append(line_array)
        
    return arranged_colors
        

def handle_interrupt_rising(channel):
    # print("Interrupt!")
    global counter_1, current_count, one_rot_time, time_per_deg, previous_micros, line_iter, delay_time_micro, rot_number
    current_count = time.time() * 1_000_000  # Get current time in microseconds
    
    rotation_end = True
    rotation_end_event.set()
    line_iter = 0
    
    one_rot_time = current_count - counter_1
    time_per_deg = one_rot_time / 360.0
    delay_time_micro = time_per_deg*degs_per_line
    previous_micros = time.time() * 1_000_000
    print("Line number {}".format(rot_number))
    rot_number = rot_number+1
            
    counter_1 = current_count


GPIO.add_event_detect(INTERRUPT_PIN, GPIO.RISING, callback=handle_interrupt_rising)


def LEDsLineTimerOptimized(line_num):
    line_iter_to_show = (line_num + LINES_TO_SHIFT + 2*NUM_DIVS)%NUM_DIVS
    global line_end_time, line_start_time
    for i in range(NUM_LEDS_TO_USE):
        color = colors_array[line_iter_to_show][i]
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
    global line_to_show_colors, line_iter, rotation_end, colors_array
    
    try:
        colors_array = arrange_colors(slices_colors)
        line_iter = 0
        while True:
            if rotation_end_event.is_set():
                rotation_end_event.clear()
                line_iter = 0
            
            # LEDsLineTimer(line_iter)  # Call function to show the line (0 is just a placeholder)
            LEDsLineTimerOptimized(line_iter)  # Call function to show the line (0 is just a placeholder)
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
