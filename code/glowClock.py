# Main software for Sierra College Robotics Club Glow Clock
# designed by Patrick Leiser
# Tested with MicroPython 1.25
import time
from machine import Pin
from machine import I2C
import neopixel
import gc
import framebuf
import _thread
import random
import math
import array

from ds3231 import DS3231   #from https://github.com/picoscratch/micropython-DS3231


#CONNECTION LAYOUT:
#LED_OUT_1: Color LEDs
#LED_OUT_2: UV LEDs
#LED_OUT_3: Reserved for future use, likely for staggered UV LED row
#LED_OUT_4: Homing sensor


#i2c pins:
sdaPin = Pin(20)
sclPin = Pin(21)

i2c = I2C(0, sda=sdaPin, scl=sclPin, freq=400000)
#using DS3231MZ RTC
ds = DS3231(i2c)

#stepper motor pins
stepPin = Pin(19, Pin.OUT)
dirPin = Pin(18, Pin.OUT)

#home sensor pin, uses LED_OUT_4 port
homeSensorPin = Pin(9, Pin.IN, Pin.PULL_DOWN)

okButtonPin = Pin(11, Pin.IN, Pin.PULL_DOWN)
backButtonPin = Pin(15, Pin.IN, Pin.PULL_DOWN)
upButtonPin = Pin(10, Pin.IN, Pin.PULL_DOWN)
downButtonPin = Pin(12, Pin.IN, Pin.PULL_DOWN)
leftButtonPin = Pin(14, Pin.IN, Pin.PULL_DOWN)
rightButtonPin = Pin(13, Pin.IN, Pin.PULL_DOWN)


#neopixel pins
num_pixels = 60
num_uv_pixels = 30

microSecondsPerStep = 750

pixels = neopixel.NeoPixel(Pin(6), num_pixels)
uv_pixels = neopixel.NeoPixel(Pin(7), num_pixels)

#print(pixels.brightness)
pixels.brightness = 0.45
pixels.auto_write = False
uv_pixels.brightness = 1.0
uv_pixels.auto_write = False


#constants: 
#dimensions of virtual and physical displays
travelSteps = 4250
stepsPerPixel = 32
bufW = int(travelSteps/stepsPerPixel)+1
bufH = 60

colorW = bufW
colorH = num_pixels

uvW = bufW
uvH = num_uv_pixels

pixelDepth = 2;
frameBuf_pixelDepth = framebuf.GS2_HMSB
maxColor = (2**pixelDepth)-1; #2 bits per pixel, values 0-3

# Shared variables for multithreading
steps_needed = 0
step_direction = 0
step_lock = _thread.allocate_lock()

stepCounterForward = 0
stepCounterHomeSkipped = 0
stepCounterReverse = 0

lastMinute = 0
lastSecond = 0

currentStage = 0

gameTargetRow = 0

isEraseCycle = False
specialModeGlobal = 0

print(gc.mem_free())
#+4 prevents value error, TODO figure out cause of that (allocation slightly too small)
fbuf = framebuf.FrameBuffer(bytearray(round((bufW+4)*(bufH)/4)), bufW, bufH, frameBuf_pixelDepth)

print(gc.mem_free())
#optional, for double-buffered frames
#fbuf2 = adafruit_framebuf.FrameBuffer(bytearray(round(bufW*bufH/4)), bufW, bufH, adafruit_framebuf.GS2_HMSB)
#print(gc.mem_free())

#    fbuf.pixel(x, y, color)

#each message can be up to 3 rows of 16 characters, or 2 rows and time
    #"1234567890123456","1234567890123456" , "1234567890123456"
messageArray = [

    ["Sierra College",  "Robotics Club!" ],
    ["Welcome To",      "Open Sauce!"],
    ["Special Action", "Dots"],
    ["Please don't",    "Touch! I'm busy"],
    ["Hello World",     "This is a TEST" ],
    ["Special Action", "Game4"],
    ["Howre you doing", "Because I'm a",     "Glow Clock!"],
    ["In your world",   "with human time"],

    ["ALL YOUR BASE",   "ARE BELONG TO US"],

    ["Special Action", "Polygons"],
    ["follow us on",  "instagram", "@sierrabeepbop"],
    ["Special Action", "Gradient"],
#    ["welcome to the",  "makerspace!"],
#    ["Narnian time:",   "Synchronized"],
    ["Special Action", "CursedPolygons"],
    ["UV + Glow Paint", "=Glow Clock!"],
    ["Special Action", "Gradient2"],


]

def scanI2C():
    devices = i2c.scan()
    if len(devices) != 0:
        print('Number of I2C devices found=',len(devices))
        for device in devices:
            print("Device Hexadecimel Address= ",hex(device))
    else:
        print("No i2c devices found")

#update to desired values, only call when intially setting clock
def setRTCTime():
    now = ds.datetime()
    print(f"setting time from {now}")
    year = 2025 # Can be yyyy or yy format
    month = 5
    mday = 9
    hour = 12 # 24 hour format only
    minute = 58
    second = 0 # Optional
    weekday = 6 # Optional
    datetime = (year, month, mday, hour, minute, second, weekday)
    ds.datetime(datetime)
    now = ds.datetime()
    print(f"setting time to {now}")



def profileTiming(label, start_ms, end_ms):
    elapsed_ms = time.ticks_diff(end_ms, start_ms) / 1000  # convert to microseconds
    print(f"{label}: {elapsed_ms:.1f} ms")

def setPixelColumn(pixelString, width, height, colX, step=1):
    scale = 255 / maxColor
    for i, y in enumerate(range(0, height-step+1, step)):
        #print("x: ",colX,"  y:",y)
        pixelVal = fbuf.pixel(colX, y)
        val = int((pixelVal * scale)) # 255 - () for inverted mode
        pixelString[i] = (val, val, val)

def homeRoutine():
    for i in range (1, (bufW*4)+10):
        uv_pixels[ i % num_uv_pixels ] = (255, 255, 255)
        uv_pixels[ (i-1) % num_uv_pixels ] = (0,0,0)
        uv_pixels.write()
        #waitForSteps()
        requestMotion(stepsPerPixel/4, 1)
    requestMotion(stepsPerPixel*2, 0) #back off one step
    waitForSteps()


def clearDisplay():
    fillDisplay(0)

def fillDisplay(newColor):
    fbuf.fill(newColor)
    #fbuf.rect(0,0,bufW,bufH-2,newColor)


def renderLogo():
    fbuf.text("Sierra College",2,1,maxColor)
    fbuf.text("Robotics Club!",2,10,maxColor)
    renderTime()
    #fbuf.text("Hi",2,18,maxColor)
    
def renderText(text, x, y, color):
    fbuf.text(text, x, y, color)

def renderTime():
    (year, month, day, weekday, hour, minute, second, zero) = ds.datetime()
    print(f"it is {hour}:{minute}")
    #fbuf.fill(1)
    #erase the time field
    minuteSpacer = ""
    fbuf.rect(0,19, bufW, 11, 0, True)
    if hour > 12:
        hour = hour - 12
    if minute < 10:
        minuteSpacer="0"
    fbuf.text(f"it is {hour}:{minuteSpacer}{minute}",2,20,maxColor)
    drawPolygon((int(second/6)%10)+1, 110, 24,  7,  maxColor)


#handle button presses and other real-time rendering
def handleButtons(xPixel):
    global isEraseCycle
    global specialModeGlobal
    if(okButtonPin.value()):
        for j in range(0, num_uv_pixels):
            uv_pixels[j] = (255, 255, 255)
    if(backButtonPin.value()):
        for j in range(0, num_uv_pixels):
            uv_pixels[j] = (0, 0, 0)
    if(upButtonPin.value()):
        for j in range(0, num_uv_pixels):
            uv_pixels[j] = (170, 170, 170)
    if(downButtonPin.value()):
        for j in range(0, num_uv_pixels):
            uv_pixels[j] = (85, 85, 85)
    if(specialModeGlobal == 1):
        for j in range(0, num_uv_pixels):
            x = int(255*(30*xPixel/bufW)%30)
            uv_pixels[j] = (x,x,x)
    if(specialModeGlobal == 2):
        for j in range(0, num_uv_pixels):
            x = int(255*(30*xPixel+j/bufW)%30)
            uv_pixels[j] = (x,x,x)
    if(isEraseCycle and (specialModeGlobal!=1 and specialModeGlobal!=2)):
        #print("erase cycle")
        for j in range(0, num_uv_pixels):
            uv_pixels[j] = (255, 255, 255)

def drawBufferForwards():
     global stepCounterForward
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
         handleButtons(i)
         uv_pixels.write()
         #t3 = time.ticks_us()
         #waitForSteps()
         requestMotion(stepsPerPixel, 1) #spends ~25ms moving 50 steps
         #t4 = time.ticks_us()
         #profileTiming("setPixelColumn", t0, t1)
         #profileTiming("debugPrints", t1, t2)
         #profileTiming("uvpixels.show", t2, t3)
         #profileTiming("motor steps", t3, t4)

def drawBufferBackwards():
    global stepCounterReverse
    for i in range (bufW-1, 1, -1):
         setPixelColumn(pixels, colorW, colorH, i)
         setPixelColumn(uv_pixels, uvW, uvH, i)
         handleButtons(i)
         uv_pixels.write()
         #waitForSteps()
         requestMotion(stepsPerPixel, 0) #spends ~25ms moving 50 steps

def drawRandomDots():
    clearDisplay()
    for i in range(0,256):
        fbuf.pixel(random.randint(0, bufW), random.randint(0, bufH), random.randint(1, maxColor))

def setupGame4():
    clearDisplay()
    gameTargetRow = random.randint(0, num_uv_pixels)
    fbuf.hline(0, gameTargetRow, bufW, maxColor)
    fbuf.line(0,0, bufW, num_uv_pixels, maxColor)

def drawRandomPolygons():
    clearDisplay()
    for i in range(0,25):
        drawPolygon(random.randint(0, 10), random.randint(0, bufW), random.randint(0, bufH),  random.randint(1, 10), random.randint(1, maxColor))


def drawCursedPolygons():
    clearDisplay()
    for i in range(0,35):
        drawPolygon(random.randint(0, 10), random.randint(1, bufW), random.randint(0, bufW), random.randint(0, bufH), random.randint(1, maxColor))

def activateGradient():
    global specialModeGlobal
    specialModeGlobal = 1


def setNewMessage(minute):
    global specialModeGlobal
    global currentStage
    messageIndex = currentStage % len(messageArray)
    clearDisplay()
    height = 1
    if messageArray[messageIndex][0] == "Special Action":
        if messageArray[messageIndex][1] == "Dots":
            drawRandomDots()
        elif messageArray[messageIndex][1] == "Game4":
            setupGame4()
        elif messageArray[messageIndex][1] == "Polygons":
            drawRandomPolygons()
        elif messageArray[messageIndex][1] == "CursedPolygons":
            drawCursedPolygons()
        elif messageArray[messageIndex][1] == "Gradient":
            specialModeGlobal = 1
        elif messageArray[messageIndex][1] == "Gradient2":
            specialModeGlobal = 2
            
    else:
        for message in messageArray[messageIndex]:
            renderText(message, 2, height, maxColor)
            height = height + 9
        #only write the time if there's room
        if (len(messageArray[messageIndex]) < 3):
            renderTime()

def drawPolygon(n, cx, cy, radius, color):
    verts = array.array('h', [])
    for i in range(n):
        theta = 2 * math.pi * i / n
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        verts.append(int(round(x)))
        verts.append(int(round(y/2)))
    fbuf.poly(cx, cy, verts, color)

def displayUpdate():
    global isEraseCycle
    global lastMinute
    global lastSecond
    global specialModeGlobal
    global currentStage
    (year, month, day, weekday, hour, minute, second, zero) = ds.datetime()
    if (minute != lastMinute or second > (lastSecond+30)):
        isEraseCycle = True
        print("new minute! Starting erase cycle")
        currentStage = (currentStage + 1) % len(messageArray)
        lastMinute = minute
        lastSecond = second
    else:
        isEraseCycle = False
        specialModeGlobal = 0
        print("disabling erase cycle")
    setNewMessage(minute)
    fbuf.hline(0, 29, int(bufW/60*second), 255)

    
def mainLoop():
    while(True):
        #gc.collect()
        global stepCounterForward
        global stepCounterReverse
        global stepCounterHomeSkipped
        #print("Free mem:", gc.mem_free())
        #render backwards first after homing
        drawBufferBackwards()
        displayUpdate()
        drawBufferForwards()
        displayUpdate()
        #renderTime()
        print("Fwd:", stepCounterForward, "Back:", stepCounterReverse, "Skipped:", stepCounterHomeSkipped)

def waitForSteps(threshold=0):
    global steps_needed
    while True:
        with step_lock:
            #print("waiting")
            if steps_needed <= threshold:
                break
        time.sleep_us(50)  # small yield to avoid hogging the lock
        
def main():
    _thread.start_new_thread(stepperThread,())
    homeRoutine()
    scanI2C()
    #setRTCTime()   #enable only when intially updating rtc
    renderLogo()
    global stepCounterForward
    global stepCounterReverse
    global stepCounterHomeSkipped
    waitForSteps()
    stepCounterForward = 0
    stepCounterReverse = 0
    stepCounterHomeSkipped = 0
    mainLoop()
    
def stepMotor(numsteps, direction):
    dirPin.value(direction)
    global stepCounterForward
    global stepCounterReverse
    global stepCounterHomeSkipped
    for i in range(numsteps):
        if(homeSensorPin.value() == 0 and direction == 1):
            stepPin.value(0)
            stepCounterHomeSkipped = stepCounterHomeSkipped + 1
            return False
        if(direction):
            stepCounterForward=stepCounterForward+1
        else:
            stepCounterReverse=stepCounterReverse+1
        stepPin.value(1)
        time.sleep_us(microSecondsPerStep)
        stepPin.value(0)
        time.sleep_us(microSecondsPerStep)
    return True

def requestMotion(numSteps, stepDir):
    global steps_needed
    global step_direction
    if(stepDir == step_direction):
        waitForSteps(2)
    else:
        waitForSteps()
    with step_lock:
        steps_needed = steps_needed + numSteps
        step_direction = stepDir

def stepperThread():
    global steps_needed
    global step_direction
    while True:
        if steps_needed > 0:
            #print("stepping")
            takingSteps = steps_needed
            stepMotor(steps_needed, step_direction)
            
            steps_needed = steps_needed - takingSteps                


main()
print("exiting (error in main loop?)")



