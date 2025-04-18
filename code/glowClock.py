# Main software for Sierra College Robotics Club Glow Clock
# designed by Patrick Leiser
# Tested with MicroPython 1.25
import time
from machine import Pin
import neopixel
import gc
import framebuf
import _thread


#CONNECTION LAYOUT:
#LED_OUT_1: Color LEDs
#LED_OUT_2: UV LEDs
#LED_OUT_3: Reserved for future use, likely for staggered UV LED row
#LED_OUT_4: Homing sensor


#stepper motor pins
stepPin = Pin(19, Pin.OUT)
dirPin = Pin(18, Pin.OUT)

#home sensor pin, uses LED_OUT_4 port
homeSensorPin = Pin(9, Pin.IN, Pin.PULL_DOWN)

#neopixel pins
num_pixels = 60
num_uv_pixels = 30

pixels = neopixel.NeoPixel(Pin(6), num_pixels)
uv_pixels = neopixel.NeoPixel(Pin(7), num_pixels)

#print(pixels.brightness)
pixels.brightness = 0.45
pixels.auto_write = False
uv_pixels.brightness = 1.0
uv_pixels.auto_write = False


#constants: 
#dimensions of virtual and physical displays
travelSteps = 4350
stepsPerPixel = 40
bufW = int(travelSteps/stepsPerPixel)+1 #88
bufH = 60

colorW = bufW
colorH = num_pixels

uvW = bufW
uvH = num_uv_pixels

pixelDepth = 2;
frameBuf_pixelDepth = framebuf.GS2_HMSB
maxColor = (2**pixelDepth)-1; #2 bits per pixel, values 0-3

# Shared variables for multithreading
needed_steps = 0;

# Optional: create a lock for synchronization
stepping_lock = _thread.allocate_lock()


print(gc.mem_free())
#+4 prevents value error, TODO figure out cause of that (allocation slightly too small)
fbuf = framebuf.FrameBuffer(bytearray(round((bufW+4)*(bufH)/4)), bufW, bufH, frameBuf_pixelDepth)

print(gc.mem_free())
#optional, for double-buffered frames
#fbuf2 = adafruit_framebuf.FrameBuffer(bytearray(round(bufW*bufH/4)), bufW, bufH, adafruit_framebuf.GS2_HMSB)
#print(gc.mem_free())

#    fbuf.pixel(x, y, color)

def profileTiming(label, start_ms, end_ms):
    elapsed_ms = time.ticks_diff(end_ms, start_ms) / 1000  # convert to microseconds
    print(f"{label}: {elapsed_ms:.1f} ms")

def stepMotor(numsteps, direction):
    dirPin.value(direction)
    for i in range(numsteps):
        if(homeSensorPin.value() == 0 and direction == 1):
            stepPin.value(0)
            return False
        stepPin.value(1)
        time.sleep_us(600)
        stepPin.value(0)
        time.sleep_us(600)
    return True


def setPixelColumn(pixelString, width, height, colX, step=1):
    scale = 255 / maxColor
    for i, y in enumerate(range(0, height-step, step)):
        #print("x: ",colX,"  y:",y)
        pixelVal = fbuf.pixel(colX, y)
        val = int(pixelVal * scale)
        pixelString[i] = (val, val, val)

def homeRoutine():
    for i in range (1, bufW+10):
        uv_pixels[ i % num_uv_pixels ] = (255, 255, 255)
        uv_pixels[ (i-1) % num_uv_pixels ] = (0,0,0)
        uv_pixels.write()
        stepMotor(stepsPerPixel, 1)
    stepMotor(stepsPerPixel, 0) #back off one step


def clearDisplay():
    fillDisplay(0)

def fillDisplay(newColor):
    fbuf.fill(newColor)


def renderLogo():
    fbuf.text("Sierra College",2,1,maxColor)
    fbuf.text("Robotics Club!",2,10,maxColor)

def drawBufferForwards():
     for i in range (1, bufW-1):
         setPixelColumn(pixels, colorW, colorH, i)
         #t0 = time.ticks_us()
         setPixelColumn(uv_pixels, uvW, uvH, i)
         #t1 = time.ticks_us()
         #print("x:")
         #print(i)
         #print(uv_pixels)
         #t2 = time.ticks_us()
         #pixels.show()
         uv_pixels.write()
         #t3 = time.ticks_us()
         stepMotor(stepsPerPixel, 1) #spends ~25ms moving 50 steps
         #t4 = time.ticks_us()
         #profileTiming("setPixelColumn", t0, t1)
         #profileTiming("debugPrints", t1, t2)
         #profileTiming("uvpixels.show", t2, t3)
         #profileTiming("motor steps", t3, t4)

def drawBufferBackwards():
    for i in range (bufW-2, 0, -1):
         setPixelColumn(pixels, colorW, colorH, i)
         setPixelColumn(uv_pixels, uvW, uvH, i)
         uv_pixels.write()
         stepMotor(stepsPerPixel, 0) #spends ~25ms moving 50 steps

def mainLoop():
    print("startingMainLoop")
    while(True):
        print("looping")
        #gc.collect()
        #print("Free mem:", gc.mem_free())
        #render backwards first after homing
        drawBufferBackwards()
        drawBufferForwards()

def main():
    homeRoutine()
    renderLogo()
    mainLoop()

main()
print("exiting (error in main loop?)")



