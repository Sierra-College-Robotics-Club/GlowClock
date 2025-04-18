# Main software for Sierra College Robotics Club Glow Clock
# designed by Patrick Leiser
# Tested with CircuitPython 9.2.x
import time
import board
import neopixel
import gc
import adafruit_framebuf
import digitalio
import asyncio


#CONNECTION LAYOUT:
#LED_OUT_1: Color LEDs
#LED_OUT_2: UV LEDs
#LED_OUT_3: Reserved for future use, likely for staggered UV LED row
#LED_OUT_4: Homing sensor


#stepper motor pins
stepPin = digitalio.DigitalInOut(board.GP19)
stepPin.direction = digitalio.Direction.OUTPUT
dirPin = digitalio.DigitalInOut(board.GP18)
dirPin.direction = digitalio.Direction.OUTPUT

#home sensor pin, uses LED_OUT_4 port
homeSensorPin = digitalio.DigitalInOut(board.GP9)
homeSensorPin.direction = digitalio.Direction.INPUT
homeSensorPin.pull = digitalio.Pull.DOWN

#neopixel pins
num_pixels = 60
num_uv_pixels = 30

pixels = neopixel.NeoPixel(board.GP6, num_pixels)
uv_pixels = neopixel.NeoPixel(board.GP7, num_pixels)

#print(pixels.brightness)
pixels.brightness = 0.45
pixels.auto_write = False
uv_pixels.brightness = 1.0
uv_pixels.auto_write = False


#constants: 
#dimensions of virtual and physical displays
travelSteps = 4350
stepsPerPixel = 50
bufW = int(travelSteps/stepsPerPixel)+1 #88
bufH = 60

colorW = bufW
colorH = num_pixels

uvW = bufW
uvH = num_uv_pixels

pixelDepth = 2;
frameBuf_pixelDepth = adafruit_framebuf.GS2_HMSB
maxColor = (2**pixelDepth)-1; #2 bits per pixel, values 0-3


print(gc.mem_free())
fbuf = adafruit_framebuf.FrameBuffer(bytearray(round(bufW*bufH/4)), bufW, bufH, frameBuf_pixelDepth)

print(gc.mem_free())
#optional, for double-buffered frames
#fbuf2 = adafruit_framebuf.FrameBuffer(bytearray(round(bufW*bufH/4)), bufW, bufH, adafruit_framebuf.GS2_HMSB)
#print(gc.mem_free())

#    fbuf.pixel(x, y, color)

def profileTiming(label, start_ns, end_ns):
    elapsed_us = (end_ns - start_ns) / 1000  # convert to microseconds
    print(f"{label}: {elapsed_us:.1f} us")

async def stepMotor(numsteps, direction):
    dirPin.value = direction
    for i in range(numsteps):
        if(homeSensorPin.value == 0 and direction == 1):
            stepPin.value = 0
            return False
        stepPin.value=1
        await asyncio.sleep(.0006)
        stepPin.value=0
        await asyncio.sleep(.0006)
    return True


def setPixelColumn(pixelString, width, height, colX, step=1):
    scale = 255 / maxColor
    for i, y in enumerate(range(0, height-step, step)):
        #print("x: ",colX,"  y:",y)
        pixelVal = fbuf.pixel(colX, y)
        val = int(pixelVal * scale)
        pixelString[i] = (val, val, val)

async def homeRoutine():
    for i in range (1, bufW+10):
        uv_pixels[ i % num_uv_pixels ] = (255, 255, 255)
        uv_pixels[ (i-1) % num_uv_pixels ] = (0,0,0)
        uv_pixels.show()
        await stepMotor(stepsPerPixel, 1)
    await stepMotor(stepsPerPixel, 0) #back off one step


def clearDisplay():
    fillDisplay(0)

def fillDisplay(newColor):
    fbuf.fill(newColor)


def renderLogo():
    fbuf.text("Sierra College",2,1,maxColor)
    fbuf.text("Robotics Club!",2,10,maxColor)

async def drawBufferForwards():
     for i in range (1, bufW-1):
         setPixelColumn(pixels, colorW, colorH, i)
         t0 = time.monotonic_ns()
         setPixelColumn(uv_pixels, uvW, uvH, i)
         t1 = time.monotonic_ns()
         #print("x:")
         #print(i)
         #print(uv_pixels)
         t2 = time.monotonic_ns()
         #pixels.show()
         uv_pixels.show()
         t3 = time.monotonic_ns()
         await stepMotor(stepsPerPixel, 1) #spends ~25ms moving 50 steps
         t4 = time.monotonic_ns()
         #profileTiming("setPixelColumn", t0, t1)
         #profileTiming("debugPrints", t1, t2)
         #profileTiming("uvpixels.show", t2, t3)
         #profileTiming("motor steps", t3, t4)

async def drawBufferBackwards():
    for i in range (bufW-2, 0, -1):
         setPixelColumn(pixels, colorW, colorH, i)
         setPixelColumn(uv_pixels, uvW, uvH, i)
         uv_pixels.show()
         await stepMotor(stepsPerPixel, 0) #spends ~25ms moving 50 steps

async def mainLoop():
    while(True):
        #render backwards first after homing
        await drawBufferBackwards()
        await drawBufferForwards()

async def main(): 
    await homeRoutine()
    renderLogo()
    await mainLoop()
    
asyncio.run(main())


