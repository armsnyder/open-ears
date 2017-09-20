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
    max_bri = 255
    red = [0.7006, 0.2993]
    while True:
        my_print('Awaiting flicker command')
        flicker.wait()
        my_print('Flickering')
        prev = bridge.get_light(lamp)['state']
        bridge.set_light(lamp, {'bri': max_bri, 'on': True, 'xy': red}, transitiontime=0)
        sleep(1)
        bridge.set_light(lamp, {'bri': prev['bri'], 'on': prev['on'], 'xy': prev['xy']},
                         transitiontime=1)
        sleep(3)  # cooldown
        flicker.clear()
