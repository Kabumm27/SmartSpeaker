import snowboydecoder
import os
import sys
import json
import signal
import random

import everloop
import web_interface

# from soco import SoCo

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import quote_plus


interrupted = False
hue_api_key = 'YOUR KEY HERE'

def audioRecorderCallback(fname):
    el.set_busy_color()

    wav_data = open(fname, "rb").read()

    try:
        url = "http://127.0.0.1:3000/api/speech"
        # url = "http://192.168.178.33:3000/api/speech"
        request = Request(url, data=wav_data)

        response = urlopen(request, timeout=1000)
        response_text = response.read().decode("utf-8")
        # result = json.loads(response_text)

        print("Response:", response_text)
        # print(result)

        intent_url = "http://127.0.0.1:3000/api/intent?q=" + quote_plus(response_text)
        intent_request = Request(intent_url)
        intent_response = urlopen(intent_request, timeout=1000)

        intent_json = json.loads(intent_response.read().decode("utf-8"))

        text = intent_json["text"]
        confidence = float(intent_json["intent"]["confidence"])
        intent = intent_json["intent"]["name"]

        print("{} detected as {} with a confidence of {}".format(text, intent, confidence))

        if confidence >= 0.5:
            # Sonos example
            # if intent == "music-pause" or intent == "music-play":
            #     my_zone = SoCo("192.168.178.26")
            #     if intent == "music-pause":
            #         my_zone.pause()
            #     elif intent == "music-play":
            #         my_zone.play()
            # elif intent == "hello":
            #     None

            if intent in ["lights-on", "lights-off"]:
                hue_data = str.encode(json.dumps({'on': "lights-on" == intent}))

                for light_id in range(1, 4):
                    hue_url = "http://192.168.2.104/api/" + hue_api_key + "/lights/" + str(light_id) + "/state"
                    hue_req = Request(hue_url, data=hue_data, method="PUT")
                    hue_response = urlopen(hue_req)

    except Exception:
        print("Could not reach server or something like that.")


    # os.remove(fname)
    el.set_idle_color()

    # return random.choice([True, False, False, False])
    return False


def detectedCallback():
    el.set_active_color()
    # cmd = 'arecord -q -r %d -f S16_LE' % RECORD_RATE
    # process = subprocess.Popen(cmd.split(' '), stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    print("Ding")


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.50)

el = everloop.Everloop()
el.set_idle_color()

# server = web_interface.start(el, detector)


print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=detectedCallback,
               audio_recorder_callback=audioRecorderCallback,
               interrupt_check=interrupt_callback,
               silent_count_threshold=15,
               sleep_time=0.01)

el.set_off()
# server.shutdown()
detector.terminate()
