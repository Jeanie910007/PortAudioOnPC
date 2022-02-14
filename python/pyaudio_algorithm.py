#!/usr/bin/python
# -*- coding: utf-8 -*-
import pyaudio
from six.moves import queue
from threading import Thread, Lock
import numpy as np
import wave
from datetime import datetime
import time
from ctypes import *
from numpy.fft import rfft as fft
from numpy.fft import irfft as ifft
from numpy import hanning
''' Audio recording parameters'''

# RUN_MODE = "rec result"
RUN_MODE = "listen result"
REC_SECOND = 5
REC_WAV_NAME = "rec_file"
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
HALF_CHUNK = int(CHUNK / 2)
REC_CHANNEL = 4
PLAY_CHANNEL = 2
delay_time = 0
first_time_Alg_setup = True
record_audio_buffer = []
processed_audio_buffer = b""
lock = Lock()
time_counter = 0
overlap = np.zeros(CHUNK)
win = hanning(CHUNK)
lowpass_out = np.zeros(CHUNK)
last_result = np.zeros(HALF_CHUNK)


class MicrophoneStream(object):  # Context Manager
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()  #FIFO
        self.closed = True
        self.recorded_buffer = []  #recorded buffer
        self.first_start = True
        self.first_fill_time = 0

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self.audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=REC_CHANNEL,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        fill_time = time.time()
        if self.first_start:
            self.first_fill_time = fill_time
            if RUN_MODE == "rec result":
                print("==== Start rec ====")
            else:
                print("==== Start playing ====")
            self.first_start = False
        self._buff.put(in_data)
        self.recorded_buffer.append(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        global record_audio_buffer
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()  #FIFO
            if chunk is None:
                return
            data = [chunk]
            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            multi_audio = []
            _data = b""  #private byte
            decoded = np.fromstring(data[0], 'Int16')  #string to array
            for c in range(REC_CHANNEL):
                temp = []
                for i in range(0, len(data[0]), 2 * REC_CHANNEL):
                    temp.append(decoded[i // 2 + c] / 32768)
                    if c == 1:
                        _data += data[0][i:i + 2]
                multi_audio.append(temp)
            #lock.acquire()
            record_audio_buffer.append(multi_audio)
            #lock.release()
            yield b"".join([_data])

    def save_audio(self, file_name):
        global processed_audio_buffer
        wf = wave.open(
            file_name + datetime.now().strftime("_%Y-%m-%d_%H_%M_%S") + ".wav",
            'wb')
        wf.setnchannels(2)
        wf.setsampwidth(self._audio_interface.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self._rate)
        wf.writeframes(b''.join([processed_audio_buffer]))
        wf.close()


class thread_processed():
    def __init__(self) -> None:
        pass

    def get_audio_loop(self, audio_generator):
        for _ in audio_generator:
            pass

    def play_processed_audio(self, play_stream):
        global processed_audio_buffer
        #lock.acquire()
        data = processed_audio_buffer[:CHUNK * 2]
        processed_audio_buffer = processed_audio_buffer[CHUNK * 2:]
        #lock.release()
        time.sleep(1)
        while True:
            if data != b'':
                play_stream.write(data)
            #lock.acquire()
            data = processed_audio_buffer[:CHUNK * 2]
            processed_audio_buffer = processed_audio_buffer[CHUNK * 2:]
            #lock.release()

    def execute_acoustic_algorithm(self):
        global record_audio_buffer, processed_audio_buffer, time_counter
        if len(record_audio_buffer) > 0:
            if RUN_MODE == "rec result":
                time_counter += 1
            current_record_buffer = record_audio_buffer.pop(
                0)  # type = [REC_CHANNEL][CHUNK]
            processed_signal = signal_algorithm().low_pass_process(
                current_record_buffer[0],
                3000)  # first channel with 1kHz lowpass filter
            if RUN_MODE == "rec result":  #if rec mode: ch1 is origin sig, ch2 is processed signal
                for i in range(CHUNK):
                    processed_audio_buffer  += (
                        int(current_record_buffer[i] * 32768) if abs(current_record_buffer[i]) < 1 else 
                        int(int(current_record_buffer[i]) * 32767)).to_bytes(2, byteorder="little", signed=True)
                    processed_audio_buffer  += (
                        int(processed_signal[i] * 32768) if abs(processed_signal[i]) < 1 else 
                        int(int(processed_signal[i]) * 32767)).to_bytes(2, byteorder="little", signed=True)
            elif RUN_MODE == "listen result":  #if listen mode: both ch1 and ch2 are processed signal
                for i in range(CHUNK):
                    processed_audio_buffer  += (
                        int(processed_signal[i] * 32768) if abs(processed_signal[i]) < 1 else 
                        int(int(processed_signal[i]) * 32767)).to_bytes(2, byteorder="little", signed=True)
                    processed_audio_buffer  += (
                        int(processed_signal[i] * 32768) if abs(processed_signal[i]) < 1 else 
                        int(int(processed_signal[i]) * 32767)).to_bytes(2, byteorder="little", signed=True)


class signal_algorithm:
    def __init__(self) -> None:
        pass

    def low_pass_process(self, input, cutoff_frequency):
        global last_result, lowpass_out, overlap, win
        cutoff_band = int(cutoff_frequency / RATE * CHUNK)
        for i in range(2):
            overlap[HALF_CHUNK:] = input[i * HALF_CHUNK:(i + 1) * HALF_CHUNK]
            after_win = win * overlap
            data = fft(after_win)
            data[cutoff_band:-1] = 0
            data = ifft(data)
            overlap[:HALF_CHUNK] = input[i * HALF_CHUNK:(i + 1) * HALF_CHUNK]
            lowpass_out[i * HALF_CHUNK:(i + 1) *
                        HALF_CHUNK] = last_result + data[:HALF_CHUNK]
            last_result = data[HALF_CHUNK:]
        return lowpass_out


def main():
    global time_counter
    tp = thread_processed()
    p = pyaudio.PyAudio()
    # PyAudio terminate
    device_total_num = p.get_host_api_info_by_index(0)['deviceCount']
    device_list = [
        p.get_device_info_by_host_api_device_index(0, _)
        for _ in range(device_total_num)
    ]
    # print(device_list)
    play_stream = p.open(format=p.get_format_from_width(2),
                         channels=PLAY_CHANNEL,
                         rate=RATE,
                         output=True,
                         output_device_index=[
                             item for item in device_list
                             if '耳機 (Conexant ISST Audio)' in item["name"]
                         ][0]['index'])

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        # wait for first frame of audio input into buffer
        while stream.first_fill_time == 0:
            pass
        # play processed audio
        if RUN_MODE == "listen result":
            Thread(target=tp.play_processed_audio,
                   args=(play_stream, ),
                   daemon=True).start()
        # loop for generator
        Thread(target=tp.get_audio_loop, args=(audio_generator, ),
               daemon=True).start()
        # # do acoustic algorithm
        while True:
            tp.execute_acoustic_algorithm()
            # if rec mode : time_counter will count to REC_SECOND sec and break the I/O
            if time_counter == int(REC_SECOND * RATE / CHUNK):
                print("==== Finish rec ====")
                break
        stream.save_audio(REC_WAV_NAME)  # if rec mode, save the rec file


if __name__ == "__main__":
    main()