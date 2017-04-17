#!/usr/bin/env python

from threading import Lock, Thread, currentThread
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from os import path, makedirs
from datetime import datetime
from time import sleep
from sys import stdout
from signal import signal, SIGINT
from sounddevice import query_devices, DeviceList, InputStream
import numpy as np
from scikits.audiolab import wavwrite


class OpenEars:
    def __init__(self):
        self._microphone = Microphone('int16', 1024)
        self._sound_buffer = SoundBuffer(self._microphone.sample_rate * 30)
        self._microphone.subscribe(self._sound_buffer,
                                   lambda *args: self._sound_buffer.write(args[0][0]))
        self._buffer_saver = BufferSaver(self._sound_buffer, self._microphone.sample_rate, 'out')
        self._server = SingleRequestServer(8080, 'save', self._buffer_saver.save)
        self._register_shutdown_handler()

    def start(self):
        my_print('Starting Open Ears')
        self._microphone.start()
        self._server.start()
        self._keep_alive()

    def _register_shutdown_handler(self):
        signal(SIGINT, self._handle_shutdown)

    def _handle_shutdown(self, *_):
        self._server.stop()
        self._microphone.stop()

    def _is_active(self):
        return self._microphone and self._microphone.is_active() and \
               self._server and self._server.is_active()

    def _keep_alive(self):
        while self._is_active():
            sleep(2)
        self._handle_shutdown()


class Microphone:
    def __init__(self, data_type, frames_per_buffer):
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


class BufferSaver:
    def __init__(self, sound_buffer, sample_rate, output_directory):
        self._sound_buffer = sound_buffer
        self._sample_rate = sample_rate
        self._output_directory = output_directory

    def save(self):
        if not path.exists(self._output_directory):
            my_print('Creating dir ' + self._output_directory)
            makedirs(self._output_directory)
        file_name = datetime.now().strftime("%m%d_%H%M%S.wav")
        full_output_path = path.join(self._output_directory, file_name)
        buffer_contents = self._sound_buffer.read()
        encoding = self.translate_numpy_data_type_to_encoding(buffer_contents.dtype)
        wavwrite(buffer_contents, full_output_path, fs=self._sample_rate, enc=encoding)
        my_print("Saved to %s" % full_output_path)

    @staticmethod
    def translate_numpy_data_type_to_encoding(data_type):
        data_type = str(data_type)
        if data_type == 'int8':
            return 'pcmu8'
        elif 'int' in data_type:
            return data_type.replace('int', 'pcm')
        else:
            return data_type


class SingleRequestServer(HTTPServer):
    def __init__(self, port, request_name, callback):
        HTTPServer.__init__(self, ('', port), self.SingleRequestHandler)
        self._port = port
        self.request_name = request_name
        self.callback = callback
        self.thread = Thread(target=self.serve_forever, name='server')

    def start(self):
        if not self.is_active():
            my_print('Starting server on port ' + str(self._port))
            self.thread.start()

    def stop(self):
        if self.is_active():
            my_print('Shutting down server')
            self.shutdown()
            self.thread.join()

    def is_active(self):
        return self.thread.isAlive()

    def __del__(self):
        self.stop()

    class SingleRequestHandler(BaseHTTPRequestHandler):
        # noinspection PyPep8Naming
        def do_GET(self):
            if self.server.request_name in self.path:
                self.server.callback()
                self.respond_to_client()
            else:
                self.send_error(404)

        def respond_to_client(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write('OK')


def my_print(message):
    print('[%s] [%s] %s' % (datetime.now().strftime("%H:%M:%S"), currentThread().getName(),
                            message))
    stdout.flush()


if __name__ == '__main__':
    OpenEars().start()
