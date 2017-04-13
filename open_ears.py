#!/usr/bin/env python

import wave
import pyaudio
import threading
import BaseHTTPServer
import os
import datetime
import time
import signal
import sys

history_seconds = 30
output_directory = 'out'
chunk_size = 1024
bit_depth = pyaudio.paInt16
channels = 1
sample_rate = 44100
port = 8080
save_command = 'save'


def main():
    audio_buffer = {
        'frames': [''] * (sample_rate * history_seconds / chunk_size),
        'cursor': 0
    }
    audio_buffer_lock = threading.Lock()

    audio_stream = [None]

    def start_stream():
        audio = pyaudio.PyAudio()

        input_device_index = 0
        for input_device_index in xrange(audio.get_device_count()):
            if audio.get_device_info_by_index(input_device_index)['maxInputChannels'] > 0:
                break
        print('Selected microphone: ' + audio.get_device_info_by_index(input_device_index)['name'])

        def stream_callback(data_in, *_):
            with audio_buffer_lock:
                write_to_buffer(data_in)
                move_cursor()
            return None, pyaudio.paContinue

        def write_to_buffer(data_in):
            audio_buffer['frames'][audio_buffer['cursor']] = data_in

        def move_cursor():
            audio_buffer['cursor'] = (audio_buffer['cursor'] + 1) % len(audio_buffer['frames'])

        print('Opening audio stream...')
        audio_stream[0] = audio.open(format=bit_depth,
                                     channels=channels,
                                     rate=sample_rate,
                                     input=True,
                                     input_device_index=input_device_index,
                                     frames_per_buffer=chunk_size,
                                     stream_callback=stream_callback)
        print('Starting audio stream...')
        audio_stream[0].start_stream()
        print("Listening on microphone")

    def save_audio_buffer_to_disk():
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        file_name = datetime.datetime.now().strftime("%m%d_%H%M%S.wav")
        full_output_path = os.path.join(output_directory, file_name)
        wave_file = wave.open(full_output_path, 'wb')
        wave_file.setnchannels(channels)
        wave_file.setsampwidth(pyaudio.get_sample_size(bit_depth))
        wave_file.setframerate(sample_rate)
        audio_to_save = get_audio_from_buffer()
        print("Saving %d bytes of data..." % len(audio_to_save))
        wave_file.writeframes(audio_to_save)
        wave_file.close()
        print("Saved last %d seconds to %s" % (history_seconds, full_output_path))

    def get_audio_from_buffer():
        with audio_buffer_lock:
            audio_after_cursor = b''.join(audio_buffer['frames'][audio_buffer['cursor']:])
            audio_before_cursor = b''.join(audio_buffer['frames'][:audio_buffer['cursor']])
        return audio_after_cursor + audio_before_cursor

    def do_shutdown_sequence(*_):
        print('Closing audio stream...')
        audio_stream[0].close()
        print('Stopping server...')
        http_server.shutdown()
        server_thread.join()
        print('Done')
        sys.exit(1)

    def register_shutdown_handler():
        signal.signal(signal.SIGINT, do_shutdown_sequence)

    def run_forever():
        while server_thread.is_alive and audio_stream[0].is_active():
            time.sleep(5)
        print('Something went wrong. Stopping...')
        do_shutdown_sequence()

    class WebHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        def do_GET(self):
            if save_command in self.path:
                save_audio_buffer_to_disk()
                self.respond_to_client()
            else:
                self.send_error(404)

        def respond_to_client(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write('Saved')

    start_stream()

    http_server = BaseHTTPServer.HTTPServer(('', port), WebHandler)
    server_thread = threading.Thread(target=http_server.serve_forever)
    server_thread.start()
    print('Started serving on port ' + str(port))

    register_shutdown_handler()
    run_forever()


if __name__ == '__main__':
    main()
