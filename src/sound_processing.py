from Queue import Full
from datetime import datetime
from math import sqrt
from multiprocessing import Queue
from os import path, makedirs

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, filtfilt

from flicker_lights import flicker
from util import my_print

SAMPLE_RATE = 44100
OUTPUT_DIRECTORY = 'out'

unfiltered_stream = Queue(1)
rms_filtered_stream = Queue(3)
final_output_stream = Queue(1)


def butter_bandpass(low_cut, high_cut, order=3):
    nyq = 0.5 * SAMPLE_RATE
    low = low_cut / nyq
    high = high_cut / nyq
    return butter(order, [low, high], btype='band')


bandpass_filter = butter_bandpass(4000, 8000)


def cheap_test(signal):
    b, a = bandpass_filter
    filtered_signal = filtfilt(b, a, signal)
    rms = sqrt(np.mean(np.square(filtered_signal)))
    return rms > 3e-4, rms


def cheap_test_process():
    while True:
        signal = unfiltered_stream.get()
        passes_test, rms = cheap_test(signal)
        if passes_test:
            try:
                rms_filtered_stream.put_nowait((signal, rms))
            except Full:
                my_print('Warning: rms_filtered_stream queue full')


def expensive_test(signal):
    return True


def expensive_test_process():
    while True:
        signal, rms = rms_filtered_stream.get()
        if expensive_test(signal):
            try:
                final_output_stream.put_nowait((signal, rms))
            except Full:
                my_print('Warning: final_output_stream queue full')


def save_clips_above_rms_threshold():
    while True:
        signal, rms = final_output_stream.get()
        flicker.set()
        if not path.exists(OUTPUT_DIRECTORY):
            my_print('Creating dir ' + OUTPUT_DIRECTORY)
            makedirs(OUTPUT_DIRECTORY)
        rms_string = str(rms).split('.')[1][:min(10, len(str(rms)))]
        file_name = '%s_%s.wav' % (datetime.now().strftime('%m%d_%H%M%S%f')[:-5], rms_string)
        full_output_path = path.join(OUTPUT_DIRECTORY, file_name)
        wavfile.write(full_output_path, SAMPLE_RATE, signal)
        my_print("Saved [rms=%s] to %s" % (rms, full_output_path))
