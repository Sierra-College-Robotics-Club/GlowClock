
from machine import Pin
from machine import I2C

import neopixel

from ds3231 import DS3231   #from https://github.com/picoscratch/micropython-DS3231

#CONNECTION LAYOUT:
#
# Each LED_OUT port has 4 pins: GND, GPIO, +5V, +12V
#   LED_OUT_1 - GPIO6: Color LEDs
#   LED_OUT_2 - GPIO7: UV LEDs
#   LED_OUT_3 - GPIO8: staggered UV LEDs
#   LED_OUT_4 - GPIO9: Homing sensor
#
# ADC_OUT Pins
#   GND
#   GPIO28-ADC2: Unused
#   GPIO27-ADC1: Unused
#   GPIO26-ADC0: Unused
#   3V3
# I2C_LCD connector
#
#   GND
#   3V3
#   SCL/GPIO21   (shared with DS3231MZ RTC)
#   SDA/GPIO22   (shared with DS3231MZ RTC)
#
# Pi Zero 40-pin Connector
#   GPIO2 through GPIO5 are exposed via this header
#   If Raspberry Pi SBC is not used, these pins can be used as GPIO
#    if only UART or i2c communication to RasPi is used, unused pins can be unpopulated and used as GPIO
#    Jumpers on underside of PCB configure whether these pins are configured as UART/I2C (default) or as SPI
#
# GPIO0 and GPIO1 go to on-board LEDs (active high)
# Active-High pushbuttons are wired to GPIO10 through GPIO15
#   GPIO10: BTN_UP
#   GPIO11: BTN_OK
#   GPIO12: BTN_DOWN
#   GPIO13: BTN_RIGHT
#   GPIO14: BTN_LEFT
#   GPIO15: BTN_BACK


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

pixels = neopixel.NeoPixel(Pin(6), num_pixels)
uv_pixels = neopixel.NeoPixel(Pin(7), num_pixels)
uv_pixels2 = neopixel.NeoPixel(Pin(8), num_pixels)

def drawBufferForwards():
     for i in range (1, bufW-1):
         #setPixelColumn(pixels, colorW, colorH, i)
         #t0 = time.ticks_us()
         setPixelColumn(uv_pixels, uvW, uvH, i+1)
         setPixelColumn(uv_pixels2, uvW, uvH, i)
         #t1 = time.ticks_us()
         #print("x:")
         #print(i)
         #print(uv_pixels)
         #t2 = time.ticks_us()
         #pixels.show()
         handleButtons(i)
         uv_pixels.write()
         uv_pixels2.write()
         #t3 = time.ticks_us()
         #waitForSteps()
         requestMotion(stepsPerPixel, 1) #spends ~25ms moving 50 steps
         #t4 = time.ticks_us()
         #profileTiming("setPixelColumn", t0, t1)
         #profileTiming("debugPrints", t1, t2)
         #profileTiming("uvpixels.show", t2, t3)
         #profileTiming("motor steps", t3, t4)

def drawBufferBackwards():
    for i in range (bufW-1, 1, -1):
         #setPixelColumn(pixels, colorW, colorH, i)
         setPixelColumn(uv_pixels, uvW, uvH, i+1)
         setPixelColumn(uv_pixels2, uvW, uvH, i)
         handleButtons(i)
         uv_pixels.write()
         uv_pixels2.write()
         #waitForSteps()
         requestMotion(stepsPerPixel, 0) #spends ~25ms moving 50 steps