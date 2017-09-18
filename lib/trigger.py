from datetime import datetime
from threading import Thread, Event

import numpy as np

from container import Startable


class Repeater(Startable):

    def __init__(self, function, interval_seconds):
        super(Repeater, self).__init__()
        self._function = function
        self._interval_seconds = interval_seconds
        self._thread_interrupt_event = Event()
        self._thread_interrupt_event.set()
        self._time_before_work = None

    def start(self):
        if self._thread_interrupt_event.isSet():
            self._thread_interrupt_event.clear()
            Thread(target=self._run, name=self.__class__.__name__).start()

    def _run(self):
        while not self._thread_interrupt_event.isSet():
            self._time_before_work = datetime.now()
            self._function()
            time_after_work = datetime.now()
            work_time = (time_after_work - self._time_before_work).total_seconds()
            time_to_wait = max(self._interval_seconds - work_time, 0)
            self._thread_interrupt_event.wait(time_to_wait)

    def stop(self):
        self._thread_interrupt_event.set()

    def is_active(self):
        return not self._thread_interrupt_event.isSet()


class PhonThresholdTrigger:
    def __init__(self, sound_buffer, phon_calculator, phon_threshold, handler, cooldown_seconds):
        self._sound_buffer = sound_buffer
        self._phon_calculator = phon_calculator
        self._phon_threshold = phon_threshold
        self._handler = handler
        self._cooldown_seconds = cooldown_seconds
        self._data = None
        self._last_process_requested = None
        self._last_process_completed = None
        self._rms_threshold_low = self._init_rms_threshold_low()
        self._rms_threshold_high = self._init_rms_threshold_high()

    def _init_rms_threshold_low(self):
        return 1

    def _init_rms_threshold_high(self):
        return 1

    def process_buffer(self):
        self._last_process_requested = datetime.now()
        if self._is_cooling_down():
            return
        self._data = self._sound_buffer.read()
        rms_volume = self.calculate_rms_volume()
        if rms_volume < self._rms_threshold_low:
            return
        if rms_volume < self._rms_threshold_high:
            phon = self._phon_calculator.calculate_phon(self._data)
            if phon < self._phon_threshold:
                return
        self._handler()
        self._last_process_completed = datetime.now()

    def _is_cooling_down(self):
        return self._last_process_completed is not None and \
               (self._last_process_requested - self._last_process_completed).total_seconds() < \
               self._cooldown_seconds

    def calculate_rms_volume(self):
        return np.mean(np.square(self._data))


def calculate_phon(sample_rate, waveform):
    n = len(waveform)
    max_bin = n / 2 - 1
    magnitudes = (np.absolute(np.fft.fft(waveform)) / n)[:max_bin]
    frequencies = np.fft.fftfreq(n, float(1) / sample_rate)[:max_bin]
    print(np.sum(freq))



class Range:
    def __init__(self, low, high):
        self.low = low
        self.high = high

    def check_for_in_range(self, value):
        return self.low <= value < self.high


class LightPulser:
    def __init__(self):
        pass

    def pulse(self):
        pass
