from time import sleep

from sounddevice import InputStream

from sound_buffer import add_frames
from util import my_print

SAMPLE_RATE = 44100
FRAMES_PER_BUFFER = 1024
DEVICE_NAME = 'USB PnP Sound Device: Audio (hw:1,0)'
CHANNELS = 1
DATA_TYPE = 'int16'
_stream = None


def _callback(in_data, frames, time, status):
    if status.input_overflow:
        my_print('Warning: Input overflow')
    add_frames(in_data[:, 0])


def run():
    global _stream
    my_print('Starting audio stream')
    _stream = InputStream(samplerate=SAMPLE_RATE,
                          device=DEVICE_NAME,
                          channels=CHANNELS,
                          dtype=DATA_TYPE,
                          callback=_callback)
    _stream.start()
    my_print('Started')
    while _stream.active:
        sleep(1)
    my_print('Stream went inactive')
