
import time
import board
import digitalio

stepPin = digitalio.DigitalInOut(board.GP19)
stepPin.direction = digitalio.Direction.OUTPUT
dirPin = digitalio.DigitalInOut(board.GP18)
dirPin.direction = digitalio.Direction.OUTPUT


print("hello")


x=0
while(True):
    x=x+1
    if(x<10000):
        dirPin.value=0
    if(x>=1000):
        dirPin.value=1
    if(x>=20000):
        x=0
    #print("high")
    stepPin.value=1
    time.sleep(.0001)
    #print("low")
    stepPin.value=0
    time.sleep(.0001)