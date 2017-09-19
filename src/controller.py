from datetime import datetime
from math import sqrt
from os import path, makedirs
from time import sleep, time

import numpy as np
from scipy.io import wavfile

from sound_buffer import get_frames
from util import my_print

SAMPLE_RATE = 44100
READ_INTERVAL = 0.5  # seconds
OUTPUT_DIRECTORY = '/out'


def do_work():
    signal = get_frames()
    rms = get_rms(signal)
    if rms > 400:
        save(signal, rms)


def get_rms(signal):
    return sqrt(np.mean(np.square(signal, dtype=np.int32)))


def save(signal, rms):
    if not path.exists(OUTPUT_DIRECTORY):
        my_print('Creating dir ' + OUTPUT_DIRECTORY)
        makedirs(OUTPUT_DIRECTORY)
    file_name = '%s_%s.wav' % (datetime.now().strftime('%m%d_%H%M%S'), int(rms))
    full_output_path = path.join(OUTPUT_DIRECTORY, file_name)
    wavfile.write(full_output_path, SAMPLE_RATE, signal)
    my_print("Saved [rms=%s] to %s" % (rms, full_output_path))


def run():
    while True:
        loop_start = time()
        do_work()
        loop_end = time()
        loop_duration = loop_end - loop_start
        sleep(max(READ_INTERVAL - loop_duration, 0))
