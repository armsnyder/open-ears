from datetime import datetime
from multiprocessing import current_process
from sys import stdout


def my_print(message):
    print('[%s] [%s] %s' % (datetime.now().strftime("%H:%M:%S"), current_process().name, message))
    stdout.flush()
