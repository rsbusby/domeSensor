

import RPi.GPIO as GPIO

from time import sleep 
import os

import commands
from datetime import datetime
import random
from math import floor

GPIO.setmode(GPIO.BCM)

# 10 inputs
pins = [11, 15 ,17,18,21,22,23,24,25]
pins = [4, 17, 18]
#GPIO.setup(11, GPIO.IN)
for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#MP = 'aplay'
MP = 'omxplayer' # --vol -1 lynx.wav --pos 18

class touchPlay(object):

    def __init__(self, pin, fileList, duration = None, name=None, timeout=20, wait=0, sustain=False):
        if not name:
            self.name = "signal" + str(pin)
        else:
            self.name = name
        self.duration = duration
        if duration and duration != 0:
            self.dOpt = ' -d ' + str(duration)
        else:
            self.dOpt = ''
        #try:
        #    self.wavFile = fileList[0]
        #except:
        #    self.wavFile = None
        self.fileList = fileList
        self.pin = pin
        self.timeout = timeout
        self.sustain = sustain
        self.lastTime = datetime.now()
        self.wait = wait
        self.mp = MP
        self.pos = 0
        self.fileDict = {}
        for f in self.fileList:
            self.fileDict[f] = self.getLength(f)
        self.wavFile = self.getFile()
        print self.wavFile   
        self.setLength()
        

    def getLength(self, soundFile):
        info = commands.getoutput("omxplayer " + str(soundFile) + " --info")
        t =  info.split("Duration:")[-1].split(',')[0]
        tt = t.split(":")
        print t
        sec = int(floor(float(tt[-1].lstrip('0'))))
        minStr =  tt[-2].lstrip('0')
        if minStr:
            minVal = int(minStr) 
        else:
            minVal = 0
        length =  int(sec + minVal * 60)#+ tt[-3]*3600
        return length
    
    def setLength(self):
        if self.wavFile:
            self.length = self.fileDict[self.wavFile]
            return True
        return False
        
    def getFile(self):
        if not len(self.fileList):
            return None
        if len(self.fileList) == 1:
            return self.fileList[0]
        #choice = random.randint(0,len(self.fileList)-1)
        choice = random.choice(list(self.fileDict.keys()))
        print "Picking " + choice
        return choice

    def setDuration(self, d):
        self.duration = d
        if d and d != 0:
            self.dOpt = ' -d ' + str(d)
        else:
            self.dOpt = ''

    def setPos(self, sec):
        print "sec " + str(sec) + "  len: " + str(self.length)
        if sec > self.length:
            self.getFile()
            self.pos = 0
            print "set to zero"
        else:
            self.pos = sec
            print "set to " + str(sec)

    def appendPos(self, delta):
        sec = float(str(delta).split(':')[-1].lstrip('0'))
        self.pos = float(self.pos) + float(sec)
        #print str(self.pos) + "  "  + str(self.length)
        if self.pos > self.length:
            self.pos = 0
        
            
    def killSound(self):
        ''' stop playing '''        
        psOut = commands.getoutput('ps -ax | grep ' + self.wavFile )
        print "killing for pin " + str(self.pin )
        print psOut
        lines = psOut.split('\n')
        for line in lines:
            pid = line.split()[0].strip()
            if 'aplay' in line or 'omxplay' in line:
                print pid
                commands.getoutput('kill -9 ' + pid )
    
    def check(self):
        #print str(self.pin)  + "  " + str(GPIO.input(self.pin) ) 

        playing = None

        print str(self.pin) + " " + str(GPIO.input(self.pin))   + "  pos: " + str(self.pos)  

        if self.wavFile:
            playing = int(commands.getoutput('ps -aux | grep ' +self.mp +' | grep ' + self.wavFile + ' | wc -l')) > 1
            
     	# if signal present
        if (GPIO.input(self.pin) == 0 ):
            print "on"
            if not playing:
                if self.pos <= 0 or self.pos >= self.length:
                    self.wavFile = self.getFile()
                    self.setLength()
                if self.wavFile:
                    if self.mp == 'aplay':
                        os.system("aplay " + self.wavFile + self.dOpt + " &")
                    else:
                        posOpt = ''
                        if self.pos:
                            posOpt = " --pos " + str(self.pos)
                        os.system("omxplayer " + self.wavFile + " " + self.dOpt + posOpt + " &")
                        print "starting " + self.wavFile
                        self.pos = self.pos - 1.5
                        self.lastTime = datetime.now()
                    #print self.name 
                #print self.duration
            #print self.name

            # keep sustaining
            if playing and self.sustain:
                now = datetime.now()
                delta = now - self.lastTime
                #print "delta " + str(delta)
                self.appendPos(delta)
                self.lastTime = datetime.now()
                #print self.pos

                #print "Sustaining " + self.name
        elif GPIO.input(self.pin) == True:
            
	        # If sustain and no recent trigger, then stop sound.
            if self.sustain and playing:
                now = datetime.now()
                delta = now - self.lastTime
                if delta.total_seconds() > self.timeout:
                    self.killSound()
                    self.appendPos(delta)
                    self.lastTime = now
                    print "kiilled"
                    print self.pos
        
        else:
            # do nothing
            p = 8



#fileList = [

#'/home/pi/sounds/moose.wav',
#'/home/pi/sounds/lynx.wav',
#'/home/pi/sounds/windy_birds.wav',
#'/home/pi/sounds/windy_birds.wav',
#'/home/pi/sounds/windy_birds.wav',
    

#]
import os
sdir = '/home/pi/domeSensor'
def filesFromDir(d, wd=None):
    if not wd:
        wd = sdir
    #print wd
    return [wd + '/' + d+'/'+ f for f in os.listdir(wd + '/' + d)]

#print os.listdir('t1')

#sys.exit()    
touchSensors = []
p1 = touchPlay(4, filesFromDir('p1'), timeout=6, sustain=True)
touchSensors.append(p1)
p2 = touchPlay(17, filesFromDir('p2'), timeout=6, sustain=True)
touchSensors.append(p2)
p3 = touchPlay(18, filesFromDir('p2'), timeout=45, sustain=True)
touchSensors.append(p3)
#t11 = touchPlay(11, filesFromDir('p1'), timeout=1, sustain=True)
#t14 = touchPlay(14, filesFromDir('p2'), timeout=1, sustain=True)
#t15 = touchPlay(15, filesFromDir('p3'), timeout=1, sustain=True)
#t17 = touchPlay(17, filesFromDir('p4'), timeout=1, sustain=True)
#t18 = touchPlay(18, filesFromDir('p5'), timeout=1, sustain=True)

#t21 = touchPlay(21, filesFromDir('t1'), 8)
#t22 = touchPlay(22, ['/home/pi/sounds/lynxno.wav'], 50)
#t23 = touchPlay(23, ['/home/pi/sounds/moose.wav'], 6)
#t24 = touchPlay(24, ['/home/pi/sounds/monkeys.wav'], 5)
#t25 = touchPlay(25, ['/home/pi/sounds/moose.wav'], 60)


while True:

    for s in touchSensors:
        s.check()

    #sleep(0.15)

    #t11.check()
    #t14.check()
    #t15.check()
    #t17.check()
    #t18.check()

    #t21.check()
    #t22.check()
    #t23.check()
    #t24.check()
    #t25.check()


    # change duration randomly each time
    #t11.setDuration(random.randint(2, 12))
    #t14.setDuration(random.randint(2, 12))
    #t15.setDuration(random.randint(2, 12))
    #t17.setDuration(random.randint(2, 12))
    #t18.setDuration(random.randint(2, 12))

    #t21.setDuration(random.randint(2, 12))
    #t22.setDuration(random.randint(4, 14))
    #t23.setDuration(random.randint(4, 14))
    #t24.setDuration(random.randint(5, 12))
    #t25.setDuration(random.randint(2, 14))        
        
