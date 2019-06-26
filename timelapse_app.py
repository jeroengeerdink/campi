#!/usr/bin/env python
# Author: Robert H Cudmore
# Web: http://robertcudmore.org
# Date: 20151205
#Purpose: Run a Flask webserver to provide a REST interface to VideoServer.py
#

'''
API
===
http://server/

http://server/startarm
http://server/stoparm

http://server/startvideo
http://server/stopvideo

http://server/timelapseon
http://server/timelapseoff

'''
import time, datetime, platform
import pprint #to print class members
import shlex
from flask import Flask, jsonify, send_file, redirect

import VideoServer

print 'starting server at:', time.strftime("%m/%d/%y"), time.strftime("%H:%M:%S")

app = Flask(__name__)

print 'starting video server'
v=VideoServer.VideoServer()
v.daemon = True
v.start()

def genericresponse():
    dateStr = time.strftime("%m/%d/%y")
    timeStr = time.strftime("%H:%M:%S")
    ret = dateStr + ' ' + timeStr + ' system running on: ' + platform.system() + '<BR>'
    ret += '<BR>'
    ret += pprint.pformat(v.__dict__).replace(',','<BR>')
    return ret

@app.route('/arm', methods=['GET'])
def startArm():
    v.startArm()
    return genericresponse()

@app.route('/disarm', methods=['GET'])
def stopArm():
    v.stopArm()
    return genericresponse()

@app.route('/start', methods=['GET'])
def startVideo():
    v.startVideo()
    return genericresponse()

@app.route('/stop', methods=['GET'])
def stopVideo():
    v.stopVideo()
    return genericresponse()

@app.route('/timelapseon', methods=['GET'])
def timelapseon():
    v.doTimelapse = 1
    return genericresponse()

@app.route('/timelapseoff', methods=['GET'])
def timelapseoff():
    v.doTimelapse = 0
    return genericresponse()

@app.route('/system', methods=['GET'])
def system():
    return genericresponse()

#redirect lastimage to address with v.lastimage filename
@app.route('/lastimage', methods=['GET'])
def lastimage():
    if v.lastimage:
        return redirect('/lastimage/' + v.lastimage)
    else:
        return 'no last image' + '<BR>' + genericresponse()

@app.route('/lastimage/<filename>')
def send_lastimage(filename):
    if '..' in filename or filename.startswith('/'):
        return 'please don\'t be nasty'
    else:
        return send_file(v.savepath + filename)

@app.route('/lastvideo')
def send_lastvideo():
    if v.savename:
        basepath = v.savepath + v.savename
        path = basepath + "_before.h264"
        print path
        print basepath
        command = shlex.split("MP4Box -add {} {}.mp4".format(path, basepath))
        print command
        try:
            #output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            output = subprocess.call(command, shell=True)
        except subprocess.CalledProcessError as e:
            print 'FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output)
        print path
        return send_file(basepath+".mp4")
    else:
        return 'no last video' + '<BR>' + genericresponse()

@app.route('/convert')
def convert_lastvideo():
    if v.savename:
        basepath = v.savepath + v.savename
        path = basepath + "_before.h264"
        print path
        print basepath
        command = shlex.split("MP4Box -add {} {}.mp4".format(path, basepath))
        print command
        try:
            #output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            output = subprocess.call(command, shell=True)
        except subprocess.CalledProcessError as e:
            print 'FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output)
        print path
        return basepath
    else:
        return 'no last video' + '<BR>' + genericresponse()

@app.route('/help', methods=['GET'])
def help():
    ret = 'arm' + '<BR>'
    ret += 'disarm' + '<BR>'
    ret += 'start' + '<BR>'
    ret += 'stop' + '<BR>'
    ret += 'timelapseon' + '<BR>'
    ret += 'timelapseoff' + '<BR>'
    ret += 'lastimage' + '<BR>'
    ret += 'latvideo' + '<BR>'
    return ret

#home page
@app.route('/', methods=['GET'])
def get_index():
    ret = pprint.pformat(v.__dict__)
    ret = ret.replace(',','<BR>')
    return ret

#start the app/webserver
if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5010, debug=True)
        #socketio.run(app, host='0.0.0.0', use_reloader=True)
        #socketio.run(app, host='0.0.0.0', port=5001, use_reloader=True)
    except:
        print 'EXITING AND AT LAST LINE'
        raise
