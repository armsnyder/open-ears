from threading import Thread
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from os import path, makedirs
from datetime import datetime
from scikits.audiolab import wavwrite

from container import Startable, my_print


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


class SingleRequestServer(HTTPServer, Startable):
    def __init__(self, port, request_name, callback):
        super(SingleRequestServer, self).__init__(('', port), SingleRequestHandler)
        self.request_name = request_name
        self.callback = callback
        self.thread = Thread(target=self.serve_forever, name='server')

    def start(self):
        if not self.is_active():
            my_print('Starting server on port ' + str(self.server_port))
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
