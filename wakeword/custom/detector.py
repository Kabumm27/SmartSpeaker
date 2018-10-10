import pyaudio
import time
import numpy as np
from threading import Thread
from scipy.io import wavfile
from ctypes import *
from contextlib import contextmanager
from .predict import load_model, predict


# Hide alsa warnings / errors
def py_error_handler(filename, line, function, err, fmt):
    pass

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass


class Detector(Thread):
    def __init__(self, model_path, detected_callback=None, speech_callback=None):
        Thread.__init__(self)

        self.detected_callback = detected_callback
        self.speech_callback = speech_callback

        self.sleep_time = 0.03
        self.max_record_length = 50

        self.wakeword_counter = 0
        self.manual_activation = False

        self._running = False

        self.chunk_size = 2048
        self.format = pyaudio.paInt16
        self.channels = 8
        self.sample_rate = 16000
        self.device_index = 2

        sample_size = pyaudio.get_sample_size(self.format) # 2 with paInt16

        self.input_buffer_size = self.sample_rate * 2
        self.input_buffer = np.zeros(0, dtype=np.int16)
        self.channel_input_buffer = [np.zeros(0, dtype=np.int16)] * self.channels
        # print("Buffer size: {} per channel".format(self.input_buffer_size))

        self.detection_buffer_size = self.sample_rate * 1 # 1 second of audio data
        self.detection_buffer = np.zeros(self.detection_buffer_size, dtype=np.int16)

        print('Loading DNN')
        self.nn_model = load_model(model_path)
        print('DNN loaded')

        self.start()


    def activate(self):
        self.manual_activation = True
    

    def run(self):
        self._running = True

        # def audio_callback(in_data, frame_count, time_info, status):
        #     # frame_count: 2048
        #     # in_data length: 4096
        #     # print(time_info["current_time"] - time_info["input_buffer_adc_time"]) # 0.128 sec
        #     # self.input_buffer.extend(in_data)
        #     data = np.frombuffer(in_data, dtype=np.int16)
        #     self.input_buffer = np.append(self.input_buffer, data)
        #     play_data = chr(0) * len(in_data)
        #     return play_data, pyaudio.paContinue

        def audio_callback_multichannel(in_data, frame_count, time_info, status):
            data = np.frombuffer(in_data, dtype=np.int16)
            data = np.reshape(data, (self.channels, frame_count), order='F')

            # Mixed Channels
            # mixed = np.average(data, axis=0).astype(np.int16)
            # self.input_buffer = np.append(self.input_buffer, mixed)

            # Single Channel
            self.input_buffer = np.append(self.input_buffer, data[0])

            play_data = chr(0) * (frame_count * 2)
            return play_data, pyaudio.paContinue

        with no_alsa_error():
            self.audio = pyaudio.PyAudio()
        self.stream_in = self.audio.open(
            input=True,
            output=False,
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            frames_per_buffer=self.chunk_size,
            input_device_index=self.device_index,
            stream_callback=audio_callback_multichannel)

        print("listening...")

        self.silence_counter = 0
        self.recorded_counter = 0
        self.is_recording = False
        self.recorded_data = np.zeros(0, dtype=np.int16)

        while self._running:
            data = np.copy(self.input_buffer)
            self.input_buffer = np.zeros(0, dtype=np.int16)

            if len(data) == 0:
                # print("sleep")
                time.sleep(self.sleep_time)
                continue

            status = self.run_detection(data)

            if status == 1:
                if self.is_recording:
                    self.silence_counter += 1
            
            if self.manual_activation and not self.is_recording:
                self.is_recording = True
                self.silence_counter = 0
                self.manual_activation = False

            if status == 3:
                # if not self.is_recording:
                #     print("recording...")
                self.is_recording = True
                self.silence_counter = 0

                if self.detected_callback:
                    self.detected_callback()

            if self.is_recording:
                self.recorded_counter += 1
                # self.recorded_data.append(data)
                self.recorded_data = np.append(self.recorded_data, data)

            if self.is_recording and (self.silence_counter >= 10 or self.recorded_counter >= self.max_record_length):
                # if self.recorded_counter >= 12:
                #     self.save_message()
                # else:
                #     print("not saved - too short")

                if self.speech_callback:
                    self.speech_callback(self.recorded_data)
                
                self.is_recording = False
                self.recorded_data = np.zeros(0, dtype=np.int16)
                self.recorded_counter = 0


    def run_detection(self, data):
        self.detection_buffer = np.append(self.detection_buffer, data)[-self.detection_buffer_size:]
        
        voice_activity = np.abs(self.detection_buffer).mean()
        if voice_activity < 70:
            # print('silence...')
            return 1 # silence detected

        if self.is_recording:
            return 2


        # print('not silence...')
        # int16 -> float32
        samples = self.detection_buffer / (2**15 - 1)
        prediction = predict(samples, self.sample_rate, self.nn_model)

        # print(prediction)
        if prediction == 0:
            self.save_wakeword('keyword')
            return 3
        else:
            self.save_wakeword('not_keyword')
            return 2

        # self.detection_buffer *= 0
        # self.voice_activity_history *= 0.8
        # self.voice_activity_history *= 0


    # def save_message(self):
    #     # save same data with removed silence
    #     filename = 'output' + str(int(time.time())) + '.wav'
    #     data = b''.join(self.recorded_data[:-6])

    #     # wf = wave.open(filename, 'wb')
    #     # wf.setnchannels(1)
    #     # wf.setsampwidth(self.audio.get_sample_size(self.format))
    #     # wf.setframerate(self.sample_rate)
    #     # wf.writeframes(data)
    #     # wf.close()
    #     # print("saved file " + filename + "; record_counter: " + str(self.recorded_counter))

    #     return filename


    def save_wakeword(self, save_dir): #, data):
        # return # Don't save anything
        self.wakeword_counter += 1
        # filename = save_dir + "/wakeword_" + str(int(time.time())) + "_" + str(self.wakeword_counter) + ".wav"
        filename = 'data/{}/{}_{}.wav'.format(save_dir, int(time.time() * 1000), self.wakeword_counter)
        # data = b"".join(wakeword_data)

        # wf = wave.open(filename, 'wb')
        # wf.setnchannels(1)
        # wf.setsampwidth(self.audio.get_sample_size(self.format))
        # wf.setframerate(self.sample_rate)
        # wf.writeframes(data)
        # wf.close()
        wavfile.write(filename, self.sample_rate, self.detection_buffer)
        # print("saved wakeword audio: " + filename)


    def terminate(self):
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()
        self._running = False


if __name__ == "__main__":
    detector = Detector('models/model_1538342008.h5')

    try:
        detector.start()
    except KeyboardInterrupt:
        print("Interrupt received, stopping…")
    finally:
        detector.terminate()