#!/usr/bin/env python

import wave
import pyaudio
import threading
import BaseHTTPServer
import os
import datetime
import time
import sys
import signal


class OpenEars:
    def __init__(self):
        self._microphone = Microphone(2, 1024)
        self._sound_buffer = SoundBuffer(self._microphone, 30)
        self._buffer_saver = BufferSaver(self._sound_buffer, 'out')
        self._server = SingleRequestServer(8080, 'save', self._buffer_saver.save)
        self._is_active = False
        self._register_shutdown_handler()

    def start(self):
        my_print('Starting Open Ears')
        self._is_active = True
        self._microphone.start()
        self._server.start()
        self._keep_alive()

    def _register_shutdown_handler(self):
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _handle_shutdown(self, *_):
        self._is_active = False
        self._server.stop()
        self._microphone.stop()

    def _keep_alive(self):
        while self._is_active:
            if not self._server.is_active():
                my_print('Problem with server')
                sys.exit(1)
            if not self._microphone.is_active():
                my_print('Problem with audio stream')
                sys.exit(1)
            time.sleep(2)


class Microphone:
    def __init__(self, sample_width, frames_per_buffer):
        self.sample_width = sample_width
        self._format = pyaudio.get_format_from_width(sample_width)
        self.frames_per_buffer = frames_per_buffer
        self._audio = pyaudio.PyAudio()
        self._device_info = None
        self._stream = None
        self._subscribers = {}
        self.channels = None
        self.index = None
        self.sample_rate = None
        self._select_microphone()

    def _select_microphone(self):
        for i in xrange(self._audio.get_device_count()):
            device_info = self._audio.get_device_info_by_index(i)
            self.channels = int(device_info['maxInputChannels'])
            self.index = int(device_info['index'])
            self.sample_rate = int(device_info['defaultSampleRate'])
            if self.channels:
                my_print('Selected microphone: ' + device_info['name'])
                break
        if not self.channels:
            raise RuntimeError("Could not find any microphones")

    def __del__(self):
        self.stop()
        if self._audio:
            self._audio.terminate()

    def start(self):
        if not self._stream:
            my_print('Starting audio stream')
            self._stream = self._audio.open(format=self._format,
                                            channels=self.channels,
                                            rate=self.sample_rate,
                                            input=True,
                                            input_device_index=self.index,
                                            frames_per_buffer=self.frames_per_buffer,
                                            stream_callback=self._callback)
        return self

    def _callback(self, *args):
        for callback in self._subscribers.values():
            callback(*args)
        return None, pyaudio.paContinue

    def stop(self):
        if self.is_active():
            my_print('Stopping audio stream')
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        return self

    def subscribe(self, caller, callback):
        my_print('Adding subscriber ' + str(caller))
        self._subscribers[caller] = callback
        return self

    def is_active(self):
        return self._stream and self._stream.is_active()


class SoundBuffer:
    def __init__(self, microphone, size_seconds):
        self.microphone = microphone
        self._frames = [''] * (microphone.sample_rate * size_seconds / microphone.frames_per_buffer)
        self._cursor = 0
        self._lock = threading.Lock()
        microphone.subscribe(self, self._callback)

    def _callback(self, data_in, *_):
        with self._lock:
            self._frames[self._cursor] = data_in
            self._cursor = (self._cursor + 1) % len(self._frames)

    def get(self):
        with self._lock:
            audio_after_cursor = b''.join(self._frames[self._cursor:])
            audio_before_cursor = b''.join(self._frames[:self._cursor])
        return audio_after_cursor + audio_before_cursor


class BufferSaver:
    def __init__(self, sound_buffer, output_directory):
        self._sound_buffer = sound_buffer
        self._output_directory = output_directory

    def save(self):
        if not os.path.exists(self._output_directory):
            my_print('Creating dir ' + self._output_directory)
            os.makedirs(self._output_directory)
        file_name = datetime.datetime.now().strftime("%m%d_%H%M%S.wav")
        full_output_path = os.path.join(self._output_directory, file_name)
        wave_file = wave.open(full_output_path, 'wb')
        wave_file.setnchannels(self._sound_buffer.microphone.channels)
        wave_file.setsampwidth(self._sound_buffer.microphone.sample_width)
        wave_file.setframerate(self._sound_buffer.microphone.sample_rate)
        audio_to_save = self._sound_buffer.get()
        my_print("Saving %d bytes of data..." % len(audio_to_save))
        wave_file.writeframes(audio_to_save)
        wave_file.close()
        my_print("Saved to %s" % full_output_path)


class SingleRequestServer(BaseHTTPServer.HTTPServer):
    def __init__(self, port, request_name, callback):
        BaseHTTPServer.HTTPServer.__init__(self, ('', port), self.SingleRequestHandler)
        self._port = port
        self.request_name = request_name
        self.callback = callback
        self.thread = threading.Thread(target=self.serve_forever, name='server')

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

    class SingleRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
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
    print('[%s] [%s] %s' % (datetime.datetime.now().strftime("%H:%M:%S"),
                            threading.currentThread().getName(), message))


if __name__ == '__main__':
    OpenEars().start()
