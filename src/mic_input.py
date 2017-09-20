from Queue import Full

import numpy as np
from numpy_ringbuffer import RingBuffer

from sound_processing import unfiltered_stream
from util import my_print

SAMPLE_RATE = 44100  # ideally could be ~16000, but the mic we're using doesn't go that low
BLOCK_SIZE = 1024
CHANNELS = 1
DATA_TYPE = 'int16'
SAMPLE_PROCESS_INTERVAL = 14700  # 2/3 the size of a full buffer, so we get some overlap

ring_buffer = RingBuffer(22050, np.int16)


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
            normalized_signal = ring_buffer.__array__().astype(np.float16, order='C') / 2**15
            try:
                unfiltered_stream.put_nowait(normalized_signal)
            except Full:
                my_print('Warning: unfiltered_stream queue full')
    my_print('Stream went inactive')
