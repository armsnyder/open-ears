from os import listdir

import numpy as np
from scipy.io import wavfile

from src.sound_processing import cheap_test, expensive_test

SAMPLE_RATE = 44100


def test_dir(dirname, expected):
    for filename in listdir(dirname):
        if filename.endswith('.wav'):
            _, x = wavfile.read(dirname + filename)
            if x.dtype == np.int16:
                x = x.astype(np.float16, order='C') / 2 ** 15
            if cheap_test(x) and expensive_test(x) != expected:
                if expected:
                    print 'False negative: ' + filename
                else:
                    print 'False positive: ' + filename


if __name__ == '__main__':
    test_dir('../out/positives/', True)
    test_dir('../out/negatives/', False)
