

import RPi.GPIO as GPIO

from time import sleep 
import os

import commands
from datetime import datetime
import random
from math import floor


class touchPlay(object):

    def __init__(self, pin, fileList, duration = None, timeout=20, sustain=False, vol=0):
        self.fileList = fileList
        self.pin = pin
        self.timeout = timeout
        self.sustain = sustain
        self.vol = vol
        if self.vol:
            self.volOpt = " --vol " + str(vol)
        else:
            self.volOpt = ''
        self.fileDict = {}
        for f in self.fileList:
            print f
            self.fileDict[f] = self.getLength(f)
        self.wavFile = self.getFile()
        print self.wavFile   
        self.setLength()
        self.iter = 0
        self.pos = 0        
        self.playing = False
        self.startTime = None
        self.lastTime = datetime.now()

    def getLength(self, soundFile):
        info = commands.getoutput("omxplayer " + str(soundFile) + " --info")
        t =  info.split("Duration:")[-1].split(',')[0]
        ts = t.split(":")
        print t

        try:
            sec = int(floor(float(ts[-1].lstrip('0').split('.')[0])))
        except:
            print "failed, length is 10"
            sec = 10
        try:
            minStr = ts[1].lstrip('0')
        except:
            # default to zero minutes
            minStr = 0
        if minStr:
            minVal = int(minStr) 
        else:
            minVal = 0
        length =  int(sec + minVal * 60)#+ ts[-3]*3600
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
        choice = random.choice(list(self.fileDict.keys()))
        print "Picking " + choice
        return choice

    def appendPos(self, delta):
        sec = float(str(delta).split(':')[-1].lstrip('0'))
        self.pos = float(self.pos) + float(sec)
        #print str(self.pos) + "  "  + str(self.length)
        if self.pos > self.length:
            self.pos = 0
            
    def killSound(self):
        ''' stop playing '''        
        psOut = commands.getoutput('ps -ax | grep ' + self.wavFile )
        #print str(pin) + " killing "
        #print psOut
        lines = psOut.split('\n')
        for line in lines:
            pid = line.split()[0].strip()
            if 'aplay' in line or 'omxplay' or 'mplay' in line:
                #print pid
                commands.getoutput('kill -9 ' + pid )
        self.playing = False
        self.startTime = None

        if self.length - self.pos  < float(self.length) / 4.0:
            self.pos = 0
    
    def check(self):

        #print str(self.pin) + " " + str(GPIO.input(self.pin))   + "  pos: " + str(self.pos)  + " " + str(self.iter)
        #self.iter += 1

        senseVal = GPIO.input(self.pin)
     	# if signal present
        now = datetime.now()
        if self.playing:
            delta = now - self.startTime
            if delta.total_seconds() > self.length:
                self.playing = False
                self.pos = 0
                self.startTime = None


        if senseVal == 0:
            #print "on"
            if not self.playing:
                if self.pos <= 0 or self.pos >= self.length:
                    self.wavFile = self.getFile()
                    self.setLength()
                if self.wavFile:
                    if self.pos <= 0 and not self.sustain:
                        os.system("aplay " + self.wavFile + " &")
                        print "starting " + self.wavFile + " " #+ str(self.iter)
                    else:
                        posOpt = ''
                        if self.pos:
                            #posOpt = " --pos " + str(self.pos) + ' '
                            posOpt = ' -ss ' + str(self.pos) + ' '
                            print 'posOpt: ' +  posOpt
                        outStr = " > /dev/null 2>&1 "
                        #os.system("omxplayer --no-osd " + self.wavFile + " " + posOpt + self.volOpt + outStr + " &")
                        os.system('mplayer ' + posOpt + self.wavFile + ' &')
                        print "starting " + self.wavFile + " with mplayer " #+ str(self.iter)
                        # adjust pos because omxplayer takes a while to start
                        self.pos = self.pos - 1.5
                    #now = datetime.now()
                    self.lastTime = now
                    self.playing = True
                    self.startTime = now

            if self.playing and self.sustain:
                self.lastTime = now

        else: # senseVal == 1:
            # If sustaining, but no recent trigger, then stop sound.
            if self.sustain and self.playing:
                #now = datetime.now()
                delta = now - self.startTime
                print 'Stoppping....' + str(self.pin) + " " + str(self.timeout - delta.total_seconds())
                if delta.total_seconds() > self.timeout:
                    self.appendPos(delta)
                    self.killSound()
                    print str(self.pin) + " killed at " + str(self.pos)
                    self.lastTime = now
                    
                

