import collections
import pyaudio
import time
import wave
import numpy as np
import webrtcvad
from scipy.io import wavfile
from ctypes import *
from contextlib import contextmanager
from predict import load_model, predict


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


# class RingBuffer(object):
#     def __init__(self, size=4096):
#         self._buf = collections.deque(maxlen=size)

#     def extend(self, data):
#         self._buf.extend(data)

#     def get(self):
#         # tmp = bytes(bytearray(self._buf))
#         tmp = self._buf.copy()
#         self._buf.clear()
#         return tmp


class Detector(object):
    def __init__(self):
        self.sleep_time = 0.03
        self.max_record_length = 50

        # temp
        self.wakeword_counter = 0
        self.streak_max_start = 0

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

        self.voice_activity_history = np.zeros(0)

        # self.vad = webrtcvad.Vad()

        self.nn_model = load_model('model_1538342008.h5')
        print('Neural Network loaded')


    def start(self):
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
            data = np.reshape(data, (8, frame_count), order='F')

            mixed = np.average(data, axis=0).astype(np.int16)
            self.input_buffer = np.append(self.input_buffer, mixed)

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
        self.recorded_data = []

        while self._running is True:
            data = self.input_buffer
            if len(data) == 0:
                # print("sleep")
                time.sleep(self.sleep_time)
                continue

            status = self.run_detection(data)
            self.input_buffer = np.zeros(0, dtype=np.int16)

            if status == 1:
                if self.is_recording:
                    self.silence_counter += 1
            
            if status == 2:
                # if not self.is_recording:
                #     print("recording...")
                self.is_recording = True
                self.silence_counter = 0

            if self.is_recording:
                self.recorded_counter += 1
                self.recorded_data.append(data)

            if self.is_recording and (self.silence_counter >= 10 or self.recorded_counter >= self.max_record_length):
                # if self.recorded_counter >= 12:
                #     self.save_message()
                # else:
                #     print("not saved - too short")
                
                self.is_recording = False
                self.recorded_data = []
                self.recorded_counter = 0

            # break



    def run_detection(self, data):
        self.detection_buffer = np.append(self.detection_buffer, data)[-self.detection_buffer_size:]
        # print(self.detection_buffer)

        voice_activity = np.abs(self.detection_buffer).mean()
        self.voice_activity_history = np.append(self.voice_activity_history, voice_activity)[-10:]
        # print(self.voice_activity_history.mean())
        # print(voice_activity)

        # speech_windows = []
        # window_step = 320
        # window_size = window_step * 2
        # for i in range(0, len(self.detection_buffer), window_step):
        #     if len(self.detection_buffer) >= i + window_size:
        #         is_speech = self.vad.is_speech(self.detection_buffer[i:i + window_size], self.sample_rate)
        #         speech_windows.append(is_speech)


        # # Filter to smooth out values (removes single deviant value)
        # filtered_speech = speech_windows[:]
        # # for i in range(1, len(speech_windows) - 1):
        # #     if speech_windows[i - 1] == speech_windows[i + 1]:
        # #         filtered_speech[i] = speech_windows[i - 1]

        # # Find longest streak of speech
        # streak_start = 0
        # streak_value = None
        # streak_length = 0
        # streak_max_length = 0
        # streak_max_start = 0

        # for i, is_speech in enumerate(filtered_speech):
        #     if streak_value != is_speech:
        #         if streak_value == True and streak_length > streak_max_length:
        #             streak_max_length = streak_length
        #             streak_max_start = streak_start
        #         streak_start = i
        #         streak_value = is_speech
        #         streak_length = 1
        #     else:
        #         streak_length += 1
                
        # sample_start = streak_max_start * window_step
        # sample_end = sample_start + streak_max_length * window_step

        # print(streak_max_start, streak_max_start + streak_max_length, len(filtered_speech))

        # min_sample_length = 6000
        # print(sample_end - sample_start)
        # if sample_end - sample_start < min_sample_length:
        # if self.voice_activity_history.mean() < 40:
        if voice_activity < 70:
            # print('silence...')
            return 1 # silence detected


        # print('not silence...')
        # int16 -> float32
        samples = self.detection_buffer / (2**15 - 1)
        prediction = predict(samples, self.sample_rate, self.nn_model)

        print(prediction)
        if prediction:
            self.save_wakeword('keyword')
        else:
            self.save_wakeword('not_keyword')

        # self.detection_buffer *= 0
        # self.voice_activity_history *= 0.8
        # self.voice_activity_history *= 0

        return 2


    def save_message(self):
        # save same data with removed silence
        filename = 'output' + str(int(time.time())) + '.wav'
        data = b''.join(self.recorded_data[:-6])

        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(data)
        wf.close()
        print("saved file " + filename + "; record_counter: " + str(self.recorded_counter))

        return filename


    def save_wakeword(self, save_dir): #, data):
        # return # Don't save anything
        self.wakeword_counter += 1
        # filename = save_dir + "/wakeword_" + str(int(time.time())) + "_" + str(self.wakeword_counter) + ".wav"
        filename = '{}/{}_{}.wav'.format(save_dir, int(time.time() * 1000), self.wakeword_counter)
        # data = b"".join(wakeword_data)

        # wf = wave.open(filename, 'wb')
        # wf.setnchannels(1)
        # wf.setsampwidth(self.audio.get_sample_size(self.format))
        # wf.setframerate(self.sample_rate)
        # wf.writeframes(data)
        # wf.close()
        wavfile.write(filename, self.sample_rate, self.detection_buffer)
        print("saved wakeword audio: " + filename)


    def terminate(self):
        """
        Terminate audio stream. Users can call start() again to detect.
        :return: None
        """
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()
        self._running = False


if __name__ == "__main__":
    detector = Detector()

    try:
        detector.start()
    except KeyboardInterrupt:
        print("Interrupt received, stopping…")
    finally:
        detector.terminate()