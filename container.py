from signal import signal, SIGINT
from abc import ABCMeta, abstractmethod
from datetime import datetime
from sys import stdout, exit
from threading import currentThread, Event


class Startable:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def is_active(self):
        pass


class Container(Startable):

    def __init__(self, name='', query_children_interval_seconds=2):
        super(Container, self).__init__()
        self.name = name
        self.query_children_interval_seconds = query_children_interval_seconds
        self._children = []
        self._register_shutdown_handler()
        self._stop_event = Event()
        self._stop_event.set()

    def _register_shutdown_handler(self):
        signal(SIGINT, lambda *_: self.stop())

    def start(self):
        if self._stop_event.isSet():
            self._stop_event.clear()
            my_print('Starting ' + self.name)
            for child in self._children:
                child.start()
            self._keep_alive()

    def _keep_alive(self):
        while not self._stop_event.isSet():
            if not self.is_active():
                self.stop()
                exit(1)
            self._stop_event.wait(self.query_children_interval_seconds)

    def stop(self):
        if not self._stop_event.isSet():
            self._stop_event.set()
            for child in self._children:
                child.stop()

    def is_active(self):
        for child in self._children:
            if not child.is_active():
                return False
        return True

    def register(self, *startables):
        self._children.extend(startables)


def my_print(message):
    print('[%s] [%s] %s' % (datetime.now().strftime("%H:%M:%S"), currentThread().getName(),
                            message))
    stdout.flush()
