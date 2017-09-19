import sys
from unittest import TestCase

import numpy as np
from numpy.testing import assert_array_equal

sound_buffer = None


class Test(TestCase):
    def setUp(self):
        global sound_buffer
        sound_buffer = __import__('src.sound_buffer', globals(), locals(), [''], -1)

    def tearDown(self):
        del sys.modules[sound_buffer.__name__]

    def test_write_full_buffer(self):
        sample = np.random.random_sample(22500).astype(np.int16)
        sound_buffer.add_frames(sample)
        result = sound_buffer.get_frames()
        assert_array_equal(sample, result)

    def test_write_full_buffer_twice(self):
        sample = np.random.random_sample(22500).astype(np.int16)
        sound_buffer.add_frames(sample)
        sample = np.random.random_sample(22500).astype(np.int16)
        sound_buffer.add_frames(sample)
        result = sound_buffer.get_frames()
        assert_array_equal(sample, result)
