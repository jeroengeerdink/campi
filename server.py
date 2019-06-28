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
import subprocess
from flask import Flask, jsonify, send_file, redirect, request
import os, shutil
import os.path


import VideoEventServer

print 'starting server at:', time.strftime("%m/%d/%y"), time.strftime("%H:%M:%S")

app = Flask(__name__)

print 'starting video server'
v=VideoEventServer.VideoServer()
v.daemon = True
v.start()

def purgeFolder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

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
    return '{"status": "armed"}'

@app.route('/disarm', methods=['GET'])
def stopArm():
    v.stopArm()
    return '{"status": "disarmed"}'

@app.route('/video')
def send_lastvideo():
    if v.savename:
        basepath = v.savepath + v.savename
        return send_file(basepath+".mp4", mimetype='video/mp4', attachment_filename='event.mp4', as_attachment=True, cache_timeout=-1)
    else:
        return '{"status": "no video"}'

@app.route('/log')
def log():
    filepath = v.saveBuffer()
    now = time.time()
    while (not os.path.exists(filepath + ".h264")) or (time.time()<( now + 5)):
        time.sleep(0.01)
    if filepath:
        #command = shlex.split("MP4Box -add {} {}.mp4".format(path, basepath))
        command = "MP4Box -add {}.h264 {}.mp4".format(filepath, filepath)
        print command
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            #output = subprocess.call(command, shell=True)
        except subprocess.CalledProcessError as e:
            print 'FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output)
        return '{"status": "converted", "path": "'+filepath+'"}'
    else:
        return '{"status": "error"}'

@app.route('/event')
def event():
    filepath = v.saveBuffer()
    now = time.time()
    while (not os.path.exists(filepath + ".h264")) or (time.time()<( now + 5)):
        time.sleep(0.01)
    if filepath:
        #command = shlex.split("MP4Box -add {} {}.mp4".format(path, basepath))
        command = "MP4Box -add {}.h264 {}.mp4".format(filepath, filepath)
        print command
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            #output = subprocess.call(command, shell=True)
        except subprocess.CalledProcessError as e:
            print 'FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output)
        #return '{"status": "converted", "path": "'+filepath+'"}'
        now = time.time()
        while (not os.path.exists(filepath + ".mp4")) or (time.time()<( now + 5)):
            time.sleep(0.01)
        if not os.path.exists(filepath + ".mp4"):
            return "ERROR"
        return send_file(filepath+".mp4", mimetype='video/mp4', attachment_filename='event.mp4', as_attachment=True, cache_timeout=-1)
    else:
        return '{"status": "error"}'

@app.route('/quit')
def shutdown():
    shutdown_hook = request.environ.get('werkzeug.server.shutdown')
    if shutdown_hook is not None:
        shutdown_hook()
    return Response("Bye", mimetype='text/plain')

#home page
@app.route('/', methods=['GET'])
def get_index():
    ret = pprint.pformat(v.__dict__)
    ret = ret.replace(',','<BR>')
    return ret

#start the app/webserver
if __name__ == "__main__":
    try:
        purgeFolder(v.savepath)
        app.run(host='0.0.0.0', port=5010, debug=True)
        time.sleep(3)
        v.startArm()
        #socketio.run(app, host='0.0.0.0', use_reloader=True)
        #socketio.run(app, host='0.0.0.0', port=5001, use_reloader=True)
    except:
        print 'EXITING AND AT LAST LINE'
        raise
