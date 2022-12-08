import tarfile
from os import listdir, path
from threading import Thread, Event

import numpy as np
from scipy.io import wavfile

from src.sound_processing import do_filter, find_loudest_part, extract_features_from_signal
from src.util import my_print

SAMPLE_RATE = 44100
training_data_path = path.join('dev', 'training_data')


def extract_features_from_many_files(filenames):
    index = 0
    done_event = Event()

    def report_progress():
        total = len(filenames)
        timeout = 5
        while not done_event.isSet():
            done_event.wait(timeout)
            my_print('%d/%d' % (index, total))

    Thread(target=report_progress).start()
    result = []
    for filename in filenames:
        result.append(extract_features_from_file(filename))
        index += 1
    done_event.set()
    return np.vstack(result)


def extract_features_from_file(filename):
    signal = read_wav_file_into_float_array(filename)
    filtered_signal = do_filter(signal)
    signal = find_loudest_part(signal, filtered_signal)
    return extract_features_from_signal(signal)


def read_wav_file_into_float_array(filename):
    _, signal = wavfile.read(filename)
    if signal.dtype == np.int16:
        signal = signal.astype(np.float16, order='C') / 2 ** 15
    return signal


def get_wav_files_in_directory(dirname):
    return [path.join(dirname, filename) for filename in listdir(dirname)
            if filename.endswith('.wav')]


def untar_training_files():
    if not path.isdir(training_data_path):
        my_print('Extracting training data')
        with tarfile.open(path.join('dev', 'training_data.tar.gz')) as f:
            
            import os
            
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(f, "dev")


def get_all_positive_training_files():
    untar_training_files()
    return get_wav_files_in_directory(path.join(training_data_path, 'positives'))


def get_all_negative_training_files():
    untar_training_files()
    return get_wav_files_in_directory(path.join(training_data_path, 'negatives'))


def load_training_data():
    my_print('Loading positives...')
    positives = extract_features_from_many_files(get_all_positive_training_files())
    my_print('Loading negatives...')
    negatives = extract_features_from_many_files(get_all_negative_training_files())
    X = np.concatenate((positives, negatives))
    y = np.concatenate((np.ones(positives.shape[0], dtype=np.bool),
                        np.zeros(negatives.shape[0], dtype=np.bool)))
    return X, y
