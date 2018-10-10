import os
import signal
import time
import json
import numpy as np
from scipy.io import wavfile
from bottle import route, run, template

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import quote_plus

import sys
sys.path.append("..") # Adds higher directory to python modules path.

from hardware.matrixio.everloop.everloop import Everloop
from wakeword.custom.detector import Detector
from skills.hue_lights.lights import HueLights


# ZOE STATE
volume_level = 1.0
is_listening = True
speech_history = []
led_ring_on = True
room = 'Büro'
is_playing_music = False

last_command_timestamp = 0
last_command = None

hue = HueLights('Hue-Bridge-IP', 'Hue-API-Key')


# LED RING
led_ring = Everloop()
led_ring.set_idle()


# KEYWORD DETECTOR
def detected_callback():
    led_ring.set_listening()
    print('Ding')

def speech_callback(speech):
    led_ring.set_thinking()

    speech *= 2 # DEBUG: Increase volume
    
    try:
        # url = 'http://127.0.0.1:3000/api/speech'
        url = 'http://192.168.178.29:3000/api/speech'
        request = Request(url, data=speech.tobytes())

        response = urlopen(request, timeout=1000)
        response_text = response.read().decode('utf-8')
        # result = json.loads(response_text)

        print('Response:', response_text)
        # print(result)

        # intent_url = 'http://127.0.0.1:3000/api/intent?q=' + quote_plus(response_text)
        intent_url = 'http://192.168.178.29:3000/api/intent?q=' + quote_plus(response_text)
        intent_request = Request(intent_url)
        intent_response = urlopen(intent_request, timeout=1000)

        intent_json = json.loads(intent_response.read().decode('utf-8'))

        text = intent_json['text']
        confidence = float(intent_json['intent']['confidence'])
        intent = intent_json['intent']['name']

        print('"{}" detected as {} with a confidence of {}'.format(text, intent, confidence))

        if confidence >= 0.5:
            # Sonos example
            # if intent == 'music-pause' or intent == 'music-play':
            #     my_zone = SoCo('192.168.178.26')
            #     if intent == 'music-pause':
            #         my_zone.pause()
            #     elif intent == 'music-play':
            #         my_zone.play()
            # elif intent == 'hello':
            #     None

            if intent in ['lights-on', 'lights-off']:
                if intent == 'lights-on':
                    hue.switch_on(room)
                else:
                    hue.switch_off(room)

    except Exception as err:
        print('Could not reach server')
        print(err)

    led_ring.set_idle()

detector = Detector('../wakeword/custom/models/model_latest.h5', detected_callback, speech_callback)


# SERVER
@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

@route('/status')
def index():
    return {
        'running': True,
        'led_ring': {
            'presets': {
                'idle': list(led_ring.presets['idle'])
            }
        }
    }

@route('/remote')
def index():
    detector.activate()
    return 'Success'

run(host='0.0.0.0', port=8080, quit=True) # is blocking


print('\nShutting down...')
led_ring.terminate()
detector.terminate()

# def signal_handler(sig, frame):
#     led_ring.terminate()
#     detector.terminate()
#     print('TRL-C exit')


# signal.signal(signal.SIGINT, signal_handler)


