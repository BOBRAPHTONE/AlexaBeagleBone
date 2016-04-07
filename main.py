#! /usr/bin/env python

import os
import random
import time
import Adafruit_BBIO.GPIO as GPIO
import alsaaudio
import wave
import random
from creds import *
import requests
import json
import re
import signal
import sys
from memcache import Client

# Catch ctrl-c and clean up GPIO
def signal_handler(signal, frame):
	GPIO.cleanup()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

#Settings
button = "GPIO0_7" #GPIO Pin with button connected
led1 = "GPIO0_30"   # GPIO Pins with LED's conneted
led2 = "GPIO1_28"
device = "plughw:1" # Name of your microphone/soundcard in arecord -L

#Setup
recorded = False
servers = ["127.0.0.1:11211"]
mc = Client(servers, debug=1)
path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))

def internet_on():
    print "Checking Internet Connection"
    try:
        r =requests.get('https://api.amazon.com/auth/o2/token')
	print "Connection OK"
        return True
    except:
	print "Connection Failed"
    	return False

	
def gettoken():
	token = mc.get("access_token")
	refresh = refresh_token
	if token:
		return token
	elif refresh:
		payload = {"client_id" : Client_ID, "client_secret" : Client_Secret, "refresh_token" : refresh, "grant_type" : "refresh_token", }
		url = "https://api.amazon.com/auth/o2/token"
		r = requests.post(url, data = payload)
		resp = json.loads(r.text)
		mc.set("access_token", resp['access_token'], 3570)
		return resp['access_token']
	else:
		return False
		

def alexa():
	GPIO.output(led1, GPIO.HIGH)
	url = 'https://access-alexa-na.amazon.com/v1/avs/speechrecognizer/recognize'
	headers = {'Authorization' : 'Bearer %s' % gettoken()}
	d = {
   		"messageHeader": {
       		"deviceContext": [
           		{
               		"name": "playbackState",
               		"namespace": "AudioPlayer",
               		"payload": {
                   		"streamId": "",
        			   	"offsetInMilliseconds": "0",
                   		"playerActivity": "IDLE"
               		}
           		}
       		]
		},
   		"messageBody": {
       		"profile": "alexa-close-talk",
       		"locale": "en-us",
       		"format": "audio/L16; rate=16000; channels=1"
   		}
	}
	with open(path+'recording.wav') as inf:
		files = [
				('file', ('request', json.dumps(d), 'application/json; charset=UTF-8')),
				('file', ('audio', inf, 'audio/L16; rate=16000; channels=1'))
				]	
		r = requests.post(url, headers=headers, files=files)
	if r.status_code == 200:
		for v in r.headers['content-type'].split(";"):
			if re.match('.*boundary.*', v):
				boundary =  v.split("=")[1]
		data = r.content.split(boundary)
		for d in data:
			if (len(d) >= 1024):
				audio = d.split('\r\n\r\n')[1].rstrip('--')
		with open(path+"response.mp3", 'wb') as f:
			f.write(audio)
		GPIO.output(led2, GPIO.LOW)
		os.system('mpg123 -q {}1sec.mp3 {}response.mp3'.format(path, path))
		GPIO.output(led1, GPIO.LOW)
	else:
		GPIO.output(led1, GPIO.LOW)
		GPIO.output(led2, GPIO.LOW)
		for x in range(0, 3):
			time.sleep(.2)
			GPIO.output(led2, GPIO.HIGH)
			time.sleep(.2)
			GPIO.output(led2, GPIO.LOW)
		



def start():
	global recorded
	last = GPIO.input(button)
	while True:
		# wait for an edge event
		if recorded == False:
			print "Waiting for button press"
			GPIO.wait_for_edge(button,GPIO.BOTH)
		
		print "pressed!"	
		val = GPIO.input(button)
		if val != last:
			last = val
			if val == 1 and recorded == True:
				rf = open(path+'recording.wav', 'w') 
				rf.write(audio)
				rf.close()
				inp = None
				recorded = False
				alexa()
			elif val == 0:
				GPIO.output(led2, GPIO.HIGH)
				inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, device)
				inp.setchannels(1)
				inp.setrate(16000)
				inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
				inp.setperiodsize(500)
				audio = ""
				l, data = inp.read()
				if l:
					audio += data
				recorded = True
		elif val == 0:
			l, data = inp.read()
			if l:
				audio += data
	

if __name__ == "__main__":
	#GPIO.setwarnings(False)
	GPIO.cleanup()
	GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(led1, GPIO.OUT)
	GPIO.output(led1, GPIO.LOW)
	GPIO.setup(led2, GPIO.OUT)
	GPIO.output(led2, GPIO.LOW)
	GPIO.add_event_detect(button,GPIO.BOTH)
	while internet_on() == False:
		print "."
	token = gettoken()
	os.system('mpg123 -q {}1sec.mp3 {}hello.mp3'.format(path, path))
	for x in range(0, 3):
		time.sleep(.1)
		GPIO.output(led1, GPIO.HIGH)
		time.sleep(.1)
		GPIO.output(led1, GPIO.LOW)
	start()
