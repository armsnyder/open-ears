from multiprocessing import Event
from time import sleep

from phue import Bridge

from util import my_print

flicker = Event()


def run():
    lamp = 'Piano Lamp'
    bridge = Bridge('192.168.86.27')
    my_print('Connecting to Phillips Hue bridge')
    bridge.connect()
    my_print('Connected to bridge')
    while True:
        my_print('Awaiting flicker command')
        flicker.wait()
        my_print('Flickering')
        prev_bri = bridge.get_light(lamp, 'bri')
        prev_on = bridge.get_light(lamp, 'on')
        prev_xy = bridge.get_light(lamp, 'xy')
        bridge.set_light(lamp, {'bri': 255, 'on': True, 'xy': [0.7006, 0.2993]}, transitiontime=0)
        bridge.set_light(lamp, {'bri': prev_bri, 'on': prev_on, 'xy': prev_xy}, transitiontime=5)
        sleep(3)  # cooldown
        flicker.clear()
