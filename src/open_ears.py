from controller import run as run_controller
from flicker_lights import run as run_flicker
from mic_input import run as run_mic
from safe_threading import add_process, run as run_all
from util import my_print

if __name__ == '__main__':
    my_print('Initializing')
    add_process(run_mic)
    add_process(run_flicker)
    add_process(run_controller)
    my_print('Bootstrapping')
    run_all()
