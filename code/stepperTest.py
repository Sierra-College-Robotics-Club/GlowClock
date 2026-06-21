import time
from machine import Pin

stepPin = Pin(19, Pin.OUT)
dirPin  = Pin(18, Pin.OUT)

print("hello")


x=0
while(True):
    x=x+1
    if x < 10000:
        dirPin.value(0)
    if x >= 10000:
        dirPin.value(1)
    if x >= 20000:
        x=0
    #print("high")
    stepPin.value(1)
    time.sleep(.0001)
    #print("low")
    stepPin.value(0)
    time.sleep(.0001)