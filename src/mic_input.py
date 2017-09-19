from Queue import Full

import numpy as np
from numpy_ringbuffer import RingBuffer

from sound_processing import unfiltered_stream
from util import my_print

SAMPLE_RATE = 44100
BLOCK_SIZE = 1024
CHANNELS = 1
DATA_TYPE = 'int16'
SAMPLE_PROCESS_INTERVAL = 22500

ring_buffer = RingBuffer(44100, np.int16)


def run():
    from sounddevice import InputStream, default
    my_print('Starting audio stream')
    stream = InputStream(SAMPLE_RATE, BLOCK_SIZE, default.device, CHANNELS, DATA_TYPE)
    stream.start()
    my_print('Started stream')
    frames_accumulated = 0
    while stream.active:
        data, overflowed = stream.read(BLOCK_SIZE)
        if overflowed:
            my_print('Warning: Input overflow')
        ring_buffer.extend(data[:, 0])
        frames_accumulated += data.size
        if frames_accumulated > SAMPLE_PROCESS_INTERVAL:
            frames_accumulated = 0
            try:
                unfiltered_stream.put_nowait(ring_buffer.__array__())
            except Full:
                my_print('Warning: unfiltered_stream queue full')
    my_print('Stream went inactive')
