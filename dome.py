
import RPi.GPIO as GPIO

from time import sleep 
import os

import commands
from datetime import datetime
import random
from math import floor

from touchPlay import touchPlay

sdir = '/home/pi/domeSensor'
#sdir = '/media/TEST/sounds'

def filesFromDir(d, wd=None):
    if not wd:
        wd = sdir
    #print wd
    return [wd + '/' + d+'/'+ f for f in os.listdir(wd + '/' + d)]


GPIO.setmode(GPIO.BCM)

# 10 inputs
pins = [5, 6,13,19,26, 2, 3, 4, 17]
#pins = [4, 17, 18]
for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

touchSensors = []

p1 = touchPlay(5, filesFromDir('p1'), timeout=20, sustain=True)
touchSensors.append(p1)
p2 = touchPlay(6, filesFromDir('p2'), timeout=15, sustain=True, vol=0)
touchSensors.append(p2)
p3 = touchPlay(13, filesFromDir('p3'), timeout=15, sustain=True)
touchSensors.append(p3)
p4 = touchPlay(19, filesFromDir('p4'), timeout=15, sustain=True, vol=0)
touchSensors.append(p4)
p5 = touchPlay(26, filesFromDir('p5'), timeout=20, sustain=True)
touchSensors.append(p5)

t1 = touchPlay(2, filesFromDir('t1'), timeout=5, sustain=False)
touchSensors.append(t1)
t2 = touchPlay(3, filesFromDir('t3'), timeout=5, sustain=False)
touchSensors.append(t2)
t3 = touchPlay(4, filesFromDir('t2'), timeout=10, sustain=False)
touchSensors.append(t3)
t4 = touchPlay(17, filesFromDir('t4'), timeout=5, sustain=False)
touchSensors.append(t4)


# main loop
while True:

    for s in touchSensors:
        s.check()

    #sleep(0.15)
    #t25.setDuration(random.randint(2, 14))        
