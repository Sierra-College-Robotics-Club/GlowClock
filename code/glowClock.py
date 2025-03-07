# Simple test for NeoPixels on Raspberry Pi
import time
import board
import neopixel
import gc
import adafruit_framebuf


num_pixels = 90
num_uv_pixels = 60

pixels = neopixel.NeoPixel(board.GP6, num_pixels)
uv_pixels = neopixel.NeoPixel(board.GP7, num_pixels)

#print(pixels.brightness)
pixels.brightness = 0.45
pixels.auto_write = False
uv_pixels.brightness = 0.79
uv_pixels.auto_write = False



#constants: 
#dimensions of virtual and physical displays
bufW = 320
bufH = 60    #180 = LCM of 90 and 60

colorW = bufW
colorH = 90

uvW = bufW
uvH = 60

pixelDepth = 2;
frameBuf_pixelDepth = adafruit_framebuf.GS2_HMSB
maxColor = (2**pixelDepth)-1;

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
# 
# fbuf.pixel(5,18,maxColor)
# fbuf.pixel(5,19,maxColor)
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
fbuf.text("Robotics Club!",3,40,maxColor)



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
# 
def setPixelColumn(pixelString,physWidth, physHeight, colX):
    pixelArr = getPixelColumn(physWidth, physHeight, colX)
    for i, pixelVal in enumerate(pixelArr):
        pixelVal = int(pixelVal * (255 / maxColor))
        #print(pixelVal)
        pixelString[i]=(pixelVal,pixelVal,pixelVal)
        

while(True):
     for i in range (0, bufW-1):
         setPixelColumn(pixels, colorW, colorH, i)
         setPixelColumn(uv_pixels, uvW, uvH, i)
         print(uv_pixels)
         pixels.show()
         uv_pixels.show()
         time.sleep(0.05)
         


#pixels = getPixelColumn(colorW, colorH, 5)
#pixels.show()


