#!/usr/bin/env python

from lib.container import Container
from lib.saving import SingleRequestServer, BufferSaver

from lib.recording import Microphone, SoundBuffer, bind_buffer_to_microphone


class OpenEars(Container):
    def __init__(self):
        super(OpenEars, self).__init__('Open Ears')
        self.microphone = None
        self.server = None
        self.construct_microphone()
        self.construct_server()
        self.register(self.microphone, self.server)

    def construct_microphone(self):
        self.microphone = Microphone('int16', 1024)

    def construct_server(self):
        sound_buffer = SoundBuffer(self.microphone.sample_rate * 30)
        bind_buffer_to_microphone(sound_buffer, self.microphone)
        buffer_saver = BufferSaver(sound_buffer, self.microphone.sample_rate, 'out')
        self.server = SingleRequestServer(8080, 'save', buffer_saver.save)


if __name__ == '__main__':
    OpenEars().start()
