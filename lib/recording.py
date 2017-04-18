from threading import Lock
from sounddevice import query_devices, DeviceList, InputStream
import numpy as np

from container import Startable, my_print


class Microphone(Startable):
    def __init__(self, data_type, frames_per_buffer):
        super(Microphone, self).__init__()
        self.data_type = data_type
        self.frames_per_buffer = frames_per_buffer
        self._stream = None
        self._subscribers = {}
        self.channels = None
        self.sample_rate = None
        self._device_name = None
        self._select_microphone()

    def _select_microphone(self):
        device_info = query_devices(kind='input')
        if not device_info:
            raise RuntimeError("Could not find any microphones")
        if type(device_info) is DeviceList:
            device_info = device_info[0]
        self.channels = int(device_info['max_input_channels'])
        self.sample_rate = int(device_info['default_samplerate'])
        self._device_name = str(device_info['name'])
        my_print('Selected microphone: ' + self._device_name)

    def __del__(self):
        self.stop()

    def start(self):
        if not self._stream:
            my_print('Starting audio stream')
            self._stream = InputStream(self.sample_rate, self.frames_per_buffer,
                                       self._device_name, self.channels, self.data_type,
                                       callback=self._callback)
            self._stream.start()
        return self

    def _callback(self, *args):
        if args[3].input_overflow:
            my_print('Warning: Input overflow')
        for callback in self._subscribers.values():
            callback(args)

    def stop(self):
        if self.is_active():
            my_print('Stopping audio stream')
            self._stream.stop()
        return self

    def subscribe(self, caller, callback):
        my_print('Adding subscriber ' + caller.__class__.__name__)
        self._subscribers[caller] = callback
        return self

    def is_active(self):
        return self._stream and self._stream.active


class SoundBuffer:
    def __init__(self, size_in_samples, data_type=None, channels=None):
        self.size_in_samples = size_in_samples
        self.data_type = data_type
        self.channels = channels
        self._frames = None
        if self._initialized_with_audio_type():
            self._construct_frame_buffer()
        self._cursor = 0
        self._lock = Lock()

    def _construct_frame_buffer(self):
        self._frames = np.zeros((self.size_in_samples, self.channels), self.data_type)

    def _initialized_with_audio_type(self):
        return self.data_type is not None and self.channels is not None

    def write(self, data_in, start_index=None):
        def copy_over_full_buffer():
            np.copyto(self._frames, data_in[-len(self._frames):])
            self._cursor = 0

        def copy_with_wrapping():
            break_index = len(self._frames) - self._cursor
            end_index = len(data_in) - break_index
            np.copyto(self._frames[self._cursor:], data_in[:break_index])
            np.copyto(self._frames[:end_index], data_in[break_index:])
            self._cursor = end_index

        def copy_without_wrapping():
            np.copyto(self._frames[self._cursor:self._cursor + len(data_in)], data_in)
            self._cursor += len(data_in)

        with self._lock:
            if not self._initialized_with_audio_type():
                self.channels = data_in.shape[1]
                self.data_type = data_in.dtype
                self._construct_frame_buffer()
            if start_index:
                self._cursor = start_index
            if len(data_in) > len(self._frames):
                copy_over_full_buffer()
            elif self._cursor + len(data_in) > len(self._frames):
                copy_with_wrapping()
            else:
                copy_without_wrapping()

    def read(self, start_index=None, limit=None):
        with self._lock:
            if self._frames is None:
                return np.array([])
            if not start_index:
                start_index = self._cursor
            if limit:
                limit = min(limit, len(self._frames))
            else:
                limit = len(self._frames)
            return np.roll(self._frames, -start_index, 0)[:limit]


def bind_buffer_to_microphone(sound_buffer, microphone):
    microphone.subscribe(sound_buffer, lambda *args: sound_buffer.write(args[0][0]))
