# Simple test for NeoPixels on Raspberry Pi
import time
import board
import neopixel
import gc
import adafruit_framebuf
import digitalio

#stepper motor pins
stepPin = digitalio.DigitalInOut(board.GP19)
stepPin.direction = digitalio.Direction.OUTPUT
dirPin = digitalio.DigitalInOut(board.GP18)
dirPin.direction = digitalio.Direction.OUTPUT

#neopixel pins
num_pixels = 90
num_uv_pixels = 25

pixels = neopixel.NeoPixel(board.GP6, num_pixels)
uv_pixels = neopixel.NeoPixel(board.GP7, num_pixels)

#print(pixels.brightness)
pixels.brightness = 0.45
pixels.auto_write = False
uv_pixels.brightness = 1.0
uv_pixels.auto_write = False



#constants: 
#dimensions of virtual and physical displays
travelSteps = 4250
stepsPerPixel = 50
bufW = int(travelSteps/stepsPerPixel)+1 #86
bufH = 60    #180 = LCM of 90 and 60

colorW = bufW
colorH = 90

uvW = bufW
uvH = 60

pixelDepth = 2;
frameBuf_pixelDepth = adafruit_framebuf.GS2_HMSB
maxColor = (2**pixelDepth)-1; #2 bits per pixel, values 0-3

#calculated constants
#colorHDiv = bufH / colorH
#uvHDiv = bufH / uvH
#colorWDiv = bufW / colorW
#uvWDiv = bufW / uvW

print(gc.mem_free())
#frameBuf = [[(0,0,0) for x in range(bufH)] for y in range(bufW)]
fbuf = adafruit_framebuf.FrameBuffer(bytearray(round(bufW*bufH/4)), bufW, bufH, frameBuf_pixelDepth)

print(gc.mem_free())
#optional, for double-buffered frames
#fbuf2 = adafruit_framebuf.FrameBuffer(bytearray(round(bufW*bufH/4)), bufW, bufH, adafruit_framebuf.GS2_HMSB)
#print(gc.mem_free())

#    pixel(x, y, color)
#fbuf.pixel(1,35,maxColor)
#fbuf.pixel(5,35,maxColor)
#fbuf.pixel(10,35,maxColor)
#fbuf.pixel(15,35,maxColor)
#fbuf.pixel(15,34,maxColor)
#fbuf.pixel(15,33,maxColor)

# fbuf.pixel(5,20,maxColor)
# fbuf.pixel(5,21,maxColor)
# fbuf.pixel(5,22,maxColor-1)
# fbuf.pixel(5,23,maxColor-1)
# fbuf.pixel(5,24,maxColor-1)
# fbuf.pixel(6,18,maxColor)
# fbuf.pixel(6,19,maxColor)
# fbuf.pixel(6,20,maxColor)
# fbuf.pixel(6,21,maxColor)
# fbuf.pixel(6,22,maxColor-1)
# fbuf.pixel(6,23,maxColor-1)
# fbuf.pixel(6,24,maxColor-1)
#fbuf.fill(maxColor)
#fbuf.rect(10, 10, 45, 45, maxColor, fill=True)
fbuf.text("Sierra College",2,1,maxColor)
fbuf.text("Robotics Club!",2,10,maxColor)
#fbuf.hline(0,1,35, maxColor)

def stepMotor(numsteps, direction):
    dirPin.value = direction
    for i in range(numsteps):
        stepPin.value=1
        time.sleep(.0006)
        stepPin.value=0
        time.sleep(.0006)


def getPixelColumn(physWidth, physHeight, colX):
    hDiv = bufH / physHeight
    wDiv = bufW / physWidth
    bufX = int(colX * wDiv)
    #print(hDiv)
    colVals = []
    for y in range(0, physHeight-1):
        bufY = int(y * hDiv)
        #fast but inaccurate solution:
        #print(bufX)
        #print(y*hDiv)
        colVals.append(fbuf.pixel(bufX,bufY))
        #optional TODO: get average of virtual pixels in range, rather than corner of range
    return colVals

def setPixelColumn(pixelString,physWidth, physHeight, colX):
    pixelArr = getPixelColumn(physWidth, physHeight, colX)
    for i, pixelVal in enumerate(pixelArr):
        pixelVal = int(pixelVal * (255 / maxColor))
        #print(pixelVal)
        pixelString[i]=(pixelVal,pixelVal,pixelVal)


while(True):
    for i in range (1, bufW-1):
         setPixelColumn(pixels, colorW, colorH, i)
         setPixelColumn(uv_pixels, uvW, uvH, i)
         print("x:")
         print(i)
         print(uv_pixels)
         pixels.show()
         uv_pixels.show()
         stepMotor(stepsPerPixel, 1) #spends ~25ms moving 50 steps
    for i in range (bufW-2, 0, -1):
         setPixelColumn(pixels, colorW, colorH, i)
         setPixelColumn(uv_pixels, uvW, uvH, i)
         print(uv_pixels)
         pixels.show()
         uv_pixels.show()
         stepMotor(stepsPerPixel, 0) #spends ~25ms moving 50 steps




#pixels = getPixelColumn(colorW, colorH, 5)
#pixels.show()


