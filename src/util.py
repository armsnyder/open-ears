from datetime import datetime
from sys import stdout
from threading import currentThread


def my_print(message):
    print('[%s] [%s] %s' % (datetime.now().strftime("%H:%M:%S"), currentThread().getName(),
                            message))
    stdout.flush()
