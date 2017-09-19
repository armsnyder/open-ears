from sys import exc_info, exit
from threading import Event, Thread

from util import my_print

_threads = []
_exit_event = Event()


def _target_wrapper(target):
    try:
        target()
        my_print('Finished job')
        _exit_event.set()
    except:
        my_print('Unhandled exception ' + str(exc_info()))
        _exit_event.set()


def add_process(target):
    _threads.append(Thread(target=_target_wrapper, args=[target]))


def run():
    for thread in _threads:
        thread.daemon = True
        thread.start()
    _exit_event.wait()
    my_print('Exiting')
    exit(1)
