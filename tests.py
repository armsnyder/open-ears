from unittest import TestCase
from open_ears import SoundBuffer
import numpy as np
from numpy.testing import assert_array_equal


class TestSoundBuffer(TestCase):
    def test_empty_buffer(self):
        buff = SoundBuffer(10)
        self.assertEqual(0, len(buff.read()))

    def test_single_write(self):
        buff = SoundBuffer(10)
        buff.write(np.array([[0], [5], [3], [2]], np.int16))
        assert_array_equal(np.array([[0], [0], [5], [3], [2]], np.int16), buff.read()[-5:])

    def test_single_two_channel_write(self):
        buff = SoundBuffer(10)
        buff.write(np.array([[0, 1], [5, 3]], np.int16))
        assert_array_equal(np.array([[0, 0], [0, 1], [5, 3]], np.int16), buff.read()[-3:])

    def test_double_write(self):
        buff = SoundBuffer(10)
        buff.write(np.array([[0], [5], [3], [2]], np.int16))
        buff.write(np.array([[8], [2]], np.int16))
        assert_array_equal(np.array([[0], [0], [5], [3], [2], [8], [2]], np.int16),
                           buff.read()[-7:])

    def test_double_two_channel_write(self):
        buff = SoundBuffer(10)
        buff.write(np.array([[0, 2], [5, 7]], np.int16))
        buff.write(np.array([[8, 8], [2, 0]], np.int16))
        assert_array_equal(np.array([[0, 0], [0, 2], [5, 7], [8, 8], [2, 0]], np.int16),
                           buff.read()[-5:])

    def test_wrap(self):
        buff = SoundBuffer(3)
        buff.write(np.array([[4], [5], [3], [2]], np.int16))
        assert_array_equal(np.array([[5], [3], [2]], np.int16), buff.read())

    def test_wrap_on_second_write(self):
        buff = SoundBuffer(4)
        buff.write(np.array([[4], [5], [8]], np.int16))
        buff.write(np.array([[3], [2], [9]], np.int16))
        assert_array_equal(np.array([[8], [3], [2], [9]], np.int16), buff.read())

    def test_wrap_on_second_write_two_channels(self):
        buff = SoundBuffer(3)
        buff.write(np.array([[4, 3], [5, 6]], np.int16))
        buff.write(np.array([[3, 2], [2, 0]], np.int16))
        assert_array_equal(np.array([[5, 6], [3, 2], [2, 0]], np.int16), buff.read())

    def test_wrap_twice(self):
        buff = SoundBuffer(3)
        buff.write(np.array([[3], [2]], np.int16))
        buff.write(np.array([[4], [5], [3], [2], [3], [8], [5]], np.int16))
        assert_array_equal(np.array([[3], [8], [5]], np.int16), buff.read())

    def test_wrap_then_write_again(self):
        buff = SoundBuffer(3)
        buff.write(np.array([[4], [5], [3], [2]], np.int16))
        buff.write(np.array([[7]], np.int16))
        assert_array_equal(np.array([[3], [2], [7]], np.int16), buff.read())
