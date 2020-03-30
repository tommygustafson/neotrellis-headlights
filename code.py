import math
import time
import array
import board
import busio
import audioio
import adafruit_trellis_express
import adafruit_adxl34x
import neopixel
import digitalio


################################
#
# To add:
#  - Use button to change brightness of headlights, by
#    adjusting the BRIGHTNESS variable.
#  - I am think to have a button that cycles through three
#    strengths (0.3, 0.6, 1) and then loops.  Would like to
#    adjust brightness of the trellis button

# Our keypad + neopixel driver
trellis = adafruit_trellis_express.TrellisM4Express(rotation=180)

def wheel(pos): # Input a value 0 to 255 to get a color value.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    elif pos < 85:
        return(int(pos * 3), int(255 - pos*3), 0)
    elif pos < 170:
        pos -= 85
        return(int(255 - pos*3), 0, int(pos * 3))
    else:
        pos -= 170
        return(0, int(pos * 3), int(255 - pos*3))


# Clear all pixels
trellis.pixels._neopixel.fill(0)
trellis.pixels._neopixel.show()

# Test of procedularly filling in colors
# Last column is blank, to "turn off" headlights
# total of 28 buttons, for the "wheel" function,
#  will send 255 // 28
num_of_buttons = 28
color_step = 255 // num_of_buttons
colors = []
for i in range(0, num_of_buttons):
    #print(i)
    colors.append(i*color_step)

num_row = 4
num_col = 7

for i in range(0,num_row):
    for j in range(0, num_col):
        index = (i*num_col) + j
        trellis.pixels[j,i] = wheel(colors[index])

def get_colors_index_from_pressed(pressed):
    return (pressed[0][0] * num_col) + pressed[0][1]

def is_pressed_in_color_buttons(pressed):
    if pressed[0][0] >= num_row or pressed[0][1] >= num_col:
        return False
    else:
        return True

def is_pressed_change_brightness_button(pressed):
    if pressed[0][0] == 0 and pressed[0][1] == 7:
        return True
    else:
        return False

#####
# Set up outputs for neopixel rings
#####
# Set the NeoPixel brightness
BRIGHTNESS = 0.5
brightness_options = [0.25, 0.5, 0.75, 0.99]
NUM_OF_LEDS = 24 # Change to 24 when using the rings

headlight_1 = neopixel.NeoPixel(board.SDA, NUM_OF_LEDS, brightness=BRIGHTNESS, auto_write=True)
headlight_2 = neopixel.NeoPixel(board.SCL, NUM_OF_LEDS, brightness=BRIGHTNESS, auto_write=True)

headlight_1.fill(0)
headlight_2.fill(0)

def cycle_brightness():
    global BRIGHTNESS
    #print(brightness_options.index(BRIGHTNESS))
    print("Old brightness = " + str(BRIGHTNESS))
    index = brightness_options.index(BRIGHTNESS)
    #print(len(brightness_options))
    index = index + 1
    if index >= len(brightness_options):
        index = 0
    BRIGHTNESS = brightness_options[index]
    print("New brightness = " + str(BRIGHTNESS))

while True:
    stamp = time.monotonic()
    pressed = trellis.pressed_keys
    if pressed:
        print("Pressed:", pressed)
        # See if pressed one of the color select buttons
        # -- wheel(get_colors_index_from_pressed(pressed)) gives us the tuple to send
        #    to the neopixels for color changing
        if is_pressed_in_color_buttons(pressed):
            #print(is_pressed_in_color_buttons(pressed))
            #print(wheel(get_colors_index_from_pressed(pressed)))
            #print("pressed[0][0] = " + str(pressed[0][0]) + " and [0][1] = " + str(pressed[0][1]))
            #print("index = " + str(get_colors_index_from_pressed(pressed)))

            # set blank button to color for testing, comment out when working
            trellis.pixels[7,0] = wheel(colors[get_colors_index_from_pressed(pressed)])

            ####
            # Set colors of both neopixel rings
            ####
            color_tuple = wheel(colors[get_colors_index_from_pressed(pressed)])
            print(color_tuple)
            #headlight_1.brightness = 1
            headlight_1.fill(color_tuple)
            headlight_1.show()
            #headlight_2.brightness = 1
            headlight_2.fill(color_tuple)
            headlight_2.show()


        else:
            print("pressed non-color button")
            # Now see if we pressed the change brightness button
            if is_pressed_change_brightness_button(pressed):
                print("Change brightness")
                cycle_brightness()
                headlight_1.brightness = BRIGHTNESS
                headlight_2.brightness = BRIGHTNESS
                headlight_1.show()
                headlight_2.show()
                print("Brightness changed to " + str(BRIGHTNESS))
            else:
                print("Turning off headlights")
                trellis.pixels[7,0] = 0
                headlight_1.fill(0)
                headlight_2.fill(0)
                BRIGHTNESS = brightness_options[1]
                headlight_1.brightness = BRIGHTNESS
                headlight_2.brightness = BRIGHTNESS
                headlight_1.show()
                headlight_2.show()
                print("Brightness changed to " + str(BRIGHTNESS))
        time.sleep(0.25)