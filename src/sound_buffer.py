from threading import Lock

import numpy as np

SOUND_BUFFER_SIZE = 22500  # 0.5 seconds of audio
DATA_TYPE = np.int16
_buffer = np.zeros(SOUND_BUFFER_SIZE, DATA_TYPE)
_lock = Lock()
_cursor = 0


def get_frames():
    with _lock:
        return np.roll(_buffer, -_cursor, 0)


def add_frames(frames):
    def copy_over_full_buffer():
        global _cursor
        np.copyto(_buffer, frames[-len(_buffer):])
        _cursor = 0

    def copy_with_wrapping():
        global _cursor
        break_index = len(_buffer) - _cursor
        end_index = len(frames) - break_index
        np.copyto(_buffer[_cursor:], frames[:break_index])
        np.copyto(_buffer[:end_index], frames[break_index:])
        _cursor = end_index

    def copy_without_wrapping():
        global _cursor
        np.copyto(_buffer[_cursor:_cursor + len(frames)], frames)
        _cursor += len(frames)

    with _lock:
        if len(frames) > len(_buffer):
            copy_over_full_buffer()
        elif _cursor + len(frames) > len(_buffer):
            copy_with_wrapping()
        else:
            copy_without_wrapping()
