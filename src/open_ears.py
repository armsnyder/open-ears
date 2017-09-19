from logging import INFO
from multiprocessing import Process, Event, log_to_stderr
from sys import exc_info, exit

from flicker_lights import run as run_flicker
from mic_input import run as run_mic
from sound_processing import filter_stream_by_rms, save_clips_above_rms_threshold
from util import my_print

processes = []
exit_event = Event()


def add_process(target, name):
    processes.append(Process(target=target_wrapper, args=(target,), name=name))


def target_wrapper(target):
    try:
        target()
        my_print('Finished job')
        exit_event.set()
    except:
        my_print('Unhandled exception ' + str(exc_info()))
        exit_event.set()


def run_forever():
    for process in processes:
        process.daemon = True
        process.start()
    exit_event.wait()
    my_print('Exiting')
    exit(1)


if __name__ == '__main__':
    my_print('Initializing')
    log_to_stderr(INFO)
    add_process(run_mic, 'Mic')
    add_process(run_flicker, 'Flicker')
    add_process(filter_stream_by_rms, 'RMS')
    add_process(save_clips_above_rms_threshold, 'Save')
    run_forever()