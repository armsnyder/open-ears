import pickle
from Queue import Full
from math import sqrt
from multiprocessing import Queue
from os import path
from os.path import dirname, realpath

import numpy as np
from librosa import feature
from scipy.signal import butter, filtfilt

from flicker_lights import flicker_greg
from util import my_print

SAMPLE_RATE = 44100

unfiltered_stream = Queue(1)
rms_filtered_stream = Queue(3)

classifier = None


def get_classifier():
    global classifier
    if classifier is None:
        with open(path.join(dirname(realpath(__file__)), 'classifier.p')) as f:
            classifier = pickle.load(f)
    return classifier


def butter_bandpass(low_cut, high_cut, order=3):
    nyq = 0.5 * SAMPLE_RATE
    low = low_cut / nyq
    high = high_cut / nyq
    return butter(order, [low, high], btype='band')


bandpass_filter = butter_bandpass(4000, 8000)


def cheap_test(signal):
    filtered_signal = do_filter(signal)
    rms = sqrt(np.mean(np.square(filtered_signal)))
    return rms > 2e-4, filtered_signal


def do_filter(signal):
    b, a = bandpass_filter
    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal


def cheap_test_process():
    while True:
        signal = unfiltered_stream.get()
        passes_test, filtered_signal = cheap_test(signal)
        if passes_test:
            try:
                rms_filtered_stream.put_nowait((signal, filtered_signal))
            except Full:
                my_print('Warning: rms_filtered_stream queue full')


def extract_features_from_signal(signal):
    mfccs = np.mean(feature.mfcc(y=signal, sr=SAMPLE_RATE, n_mfcc=20).T, axis=0)
    return mfccs


def find_loudest_part(signal, filtered_signal):
    i = np.argmax(np.abs(filtered_signal))
    start = max(0, i - 1000)
    end = min(signal.size, i + 6000)
    return signal[start:end]


def expensive_test(signal, filtered_signal=None):
    if not filtered_signal:
        filtered_signal = do_filter(signal)
    loudest_part = find_loudest_part(signal, filtered_signal)
    features = extract_features_from_signal(loudest_part)
    return get_classifier().predict([features])[0]


def expensive_test_process():
    while True:
        signal, filtered_signal = rms_filtered_stream.get()
        if expensive_test(signal, filtered_signal):
            flicker_greg.set()
