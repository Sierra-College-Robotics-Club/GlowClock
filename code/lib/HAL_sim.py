
import time  

timeInit = time.time() 

class SimpleTime:
    def __init__(self, seconds, minutes, hour, day, month, year, weekday):
        self.seconds = seconds
        self.minutes = minutes
        self.hour    = hour
        self.day     = day
        self.month   = month
        self.year    = year
        self.weekday = weekday
    def __str__(self):
        return f"{self.hour:02}:{self.minute:02}:{self.second:02}"

def calcTime():
    timeDiff = time.time()-timeInit
    (minutes, seconds) = divmod(timeDiff, 60)
    (hours, minutes) = divmod(minutes, 60)  
    (days,hours) = divmod(hours, 24)
    #TODO: implement calculation for months and years
    times = SimpleTime(seconds, minutes, hours, days, 0,0,0)
    return times

#attempting to simulate the interface from https://github.com/picoscratch/micropython-DS3231/blob/main/ds3231.py
class DS_RTC_SIM:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self._timebuf = bytearray(7) # Pre-allocate a buffer for the time data
        self._buf = bytearray(1) # Pre-allocate a single bytearray for re-use
        self._al1_buf = bytearray(4)
        self._al2buf = bytearray(3)
        calcTime()
    def second(self, second=None):
        if second is None:
            return calcTime().seconds
        else:
            timeInit = timeInit % 60 + second
    def minute(self, minute=None):
        if minute is None:
            return calcTime().minutes
        else:
            timeInit = timeInit % (60*60) + (minute*60)
    def hour(self, hour=None):
        if hour is None:
            return calcTime().hours
        else:
            timeInit = timeInit % (60*60*24) + (hour*60*24)
    #get/set all of datetime at once
    def datetime(self, datetime=None):
        if datetime is None:
            res = calcTime()
            return (res.year, res.month, res.day, res.weekday, res.hour, res.minutes, res.seconds, 0)
        else:
            #todo handle saving of datetime
            return False
ds = DS_RTC_SIM(None)
