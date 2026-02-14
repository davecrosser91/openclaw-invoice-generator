import signal, os
from src.Datenvalidierung.CustomExceptions import CreateProductTimeLimitReachedError


def alarm_timeout_handler(signum, frame):
    raise CreateProductTimeLimitReachedError()


def set_alarm_signal_handler(timelimit: int):
    signal.signal(signal.SIGALRM, alarm_timeout_handler)
    set_alarm(timelimit)


def set_alarm(timelimit: int):
    signal.alarm(timelimit)
