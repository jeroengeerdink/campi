#!/usr/bin/env python

import os, time, io, math, threading
from datetime import datetime #to get fractional seconds
import picamera

class VideoServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        #when this script is running, it will always be armed
        self.isArmed = 0
        self.videoStarted = 0
        self.stream = None
        self.savepath = '/home/pi/video/' + time.strftime('%Y%m%d') + '/'
        if not os.path.exists(self.savepath):
            print '\tVideoServer is making output directory:', self.savepath
            os.makedirs(self.savepath)
        self.savename = '' # the prefix to save all files
        self.bufferSeconds = 30
        self.startTime = 0 #when we start recording in run(), triggered by startVideo()
        self.doTimelapse = 0

    def getState(self):
        ret = 'a=b'
        ret += '\nc=d'
        return ret

    def startArm(self):
        print '\tVideoThread startArm()'
        if self.isArmed == 0:
            print '\tVideoServer initializing camera'
            self.camera = picamera.PiCamera()
            self.camera.resolution = (640, 480)
            self.camera.rotation = 180
            #self.camera.start_preview()
            self.camera.framerate = 30 # can be 60

            print '\tVideoServer starting circular stream'
            self.stream = picamera.PiCameraCircularIO(self.camera, seconds=self.bufferSeconds)
            self.camera.start_recording(self.stream, format='h264')

            self.isArmed = 1 #order is important, must come after we instantiate camera

    def stopArm(self):
        print '\tVideoThread stopArm()'
        timestamp = self.GetTimestamp()
        if self.isArmed == 1:
            self.isArmed = 0

            self.camera.stop_preview()
            self.camera.close()
            self.camera = None

            self.scanImageFrame = 0
            print '\tVideoServer stopArm() is done'


    def GetTimestamp(self):
        #returns integer seconds (for file names)
        return time.strftime('%Y%m%d') + '_' + time.strftime('%H%M%S')

    def GetTimestamp2(self):
        # returns fraction seconds (for log file entries)
        #datetime.datetime.now().strftime("%H:%M:%S.%f")
        return time.strftime('%Y%m%d') + '_' + datetime.now().strftime("%H%M%S.%f")

    def saveBuffer(self):
        timestamp = self.GetTimestamp()
        self.savename = timestamp.split('.')[0]
        fileName = self.savepath + self.savename
        #self.write_video(self.stream, fileName + ".h264")
        with io.open(fileName + ".h264", 'wb') as output:
            self.stream.copy_to(output, seconds=30)
        self.stream.clear()
        return fileName

    #start arm
    def run(self):
        print '\tVideoServer run() is initializing [can only call this once]'
        lasttime = time.time()
        while True:
            if self.isArmed:
                timestamp = self.GetTimestamp()
                while (self.isArmed):
                    try:
                        self.camera.wait_recording(0.005)
                    except:
                        print '\tVideoServer except clause -->>ERROR'
                print '\tVideoServer.run fell out of loop'
            time.sleep(0.05)
        print '\tVideoServer terminating [is never called]'
