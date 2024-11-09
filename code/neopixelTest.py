# Simple test for NeoPixels on Raspberry Pi
import time
import board
import neopixel


# Update this to match the number of NeoPixel LEDs connected to your board.
num_pixels = 90
num_uv_pixels = 60

pixels = neopixel.NeoPixel(board.GP6, num_pixels)
uv_pixels = neopixel.NeoPixel(board.GP7, num_pixels)

#print(pixels.brightness)
pixels.brightness = 1
uv_pixels.brightness = 1.0



pixels.fill((0, 0, 0))

i = 0;
uv_i = num_uv_pixels - 1
while(True):
    i = i+1
    uv_i = uv_i - 1
    if(i>=num_pixels):
        
        i=4
    if(uv_i<0):
        uv_pixels[0] = (0,0,0)
        uv_pixels[1] = (0,0,0)
        uv_i=num_uv_pixels-1
    pixels[i] = (255,255,255)
    uv_pixels[uv_i] = (255,255,255)
    pixels[i-1] = (255,0,0)
    pixels[i-2] = (0,255,0)
    pixels[i-3] = (0,0,255)
    pixels[i-4] = (0,0,0)
    uv_pixels[uv_i+2] = (0,0,0)


