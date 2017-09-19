from Queue import Full
from datetime import datetime
from math import sqrt
from multiprocessing import Queue
from os import path, makedirs

import numpy as np
from scipy.io import wavfile

from flicker_lights import flicker
from util import my_print

SAMPLE_RATE = 44100
OUTPUT_DIRECTORY = 'out'

unfiltered_stream = Queue(1)
rms_filtered_stream = Queue(3)


def filter_stream_by_rms():
    while True:
        signal = unfiltered_stream.get()
        rms = sqrt(np.mean(np.square(signal, dtype=np.uint32)))
        if rms > 600:
            try:
                rms_filtered_stream.put_nowait((signal, rms))
            except Full:
                my_print('Warning: rms_filtered_stream queue full')


def save_clips_above_rms_threshold():
    while True:
        signal, rms = rms_filtered_stream.get()
        flicker.set()
        if not path.exists(OUTPUT_DIRECTORY):
            my_print('Creating dir ' + OUTPUT_DIRECTORY)
            makedirs(OUTPUT_DIRECTORY)
        file_name = '%s_%s.wav' % (datetime.now().strftime('%m%d_%H%M%S%f')[:-5], int(rms))
        full_output_path = path.join(OUTPUT_DIRECTORY, file_name)
        wavfile.write(full_output_path, SAMPLE_RATE, signal)
        my_print("Saved [rms=%s] to %s" % (rms, full_output_path))
