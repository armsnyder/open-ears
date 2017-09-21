from multiprocessing import Event
from socket import timeout
from time import sleep

from phue import Bridge

from util import my_print

flicker_piano = Event()
flicker_greg = Event()

bridge = Bridge()
my_print('Connecting to Phillips Hue bridge')
bridge.connect()
my_print('Connected to bridge')


def with_retries(func):
    def inner_call(*args, **kwargs):
        for attempt in xrange(3):
            try:
                return func(*args, **kwargs)
            except timeout:
                if attempt == 2:
                    raise timeout

    return inner_call


def run_piano():
    lamp = 'Piano Lamp'
    red = [0.7006, 0.2993]
    while True:
        my_print('Awaiting flicker_piano command')
        flicker_piano.wait()
        my_print('Flickering Piano')
        prev = with_retries(bridge.get_light)(lamp)['state']
        with_retries(bridge.set_light)(lamp, {'bri': 128, 'on': True, 'xy': red}, transitiontime=0)
        sleep(1)
        with_retries(bridge.set_light)(lamp,
                                       {'bri': prev['bri'], 'on': prev['on'], 'xy': prev['xy']},
                                       transitiontime=1)
        sleep(3)  # cooldown
        flicker_piano.clear()


def run_greg():
    lamp = 'Greg Lamp'
    white = [0.402, 0.3768]
    while True:
        my_print('Awaiting flicker_greg command')
        flicker_greg.wait()
        my_print('Flickering Greg')
        prev = with_retries(bridge.get_light)(lamp)['state']
        with_retries(bridge.set_light)(lamp, {'bri': 128, 'on': True, 'xy': white},
                                       transitiontime=0)
        sleep(0.2)
        with_retries(bridge.set_light)(lamp, 'on', False, 0)
        sleep(0.2)
        with_retries(bridge.set_light)(lamp, 'on', True, 0)
        sleep(0.2)
        with_retries(bridge.set_light)(lamp, 'on', False, 0)
        sleep(0.2)
        with_retries(bridge.set_light)(lamp,
                                       {'bri': prev['bri'], 'on': prev['on'], 'xy': prev['xy']},
                                       transitiontime=0)
        sleep(3)  # cooldown
        flicker_greg.clear()
