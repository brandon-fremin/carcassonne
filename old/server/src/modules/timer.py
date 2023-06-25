import time
from typing import Any, List, Dict


class TimerClock:
    func: Any
    args: List
    kwargs: Dict
    elapsed_ms: float

    # private
    _start: float
    _stop: float

    def __init__(self, func, args, kwargs) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._start = self._stop = self.elapsed_ms = 0
    
    def start(self):
        self.elapsed_ms = -1  # Invaldiate current elapsed_ms
        self._start = time.perf_counter()
        return self

    def stop(self):
        self._stop = time.perf_counter()
        self.elapsed_ms = (self._stop - self._start) * 1000
        return self
    
    def __str__(self):
        if self.elapsed_ms < 0:
            raise Exception("Cannot call str(TimerClock) before calling stop!")
        funcname = f"{self.func.__module__}::{self.func.__name__}"
        return f"Function '{funcname}' took {self.elapsed_ms:0.3f} ms"


def timer_wrapper_factory(func, callback):
    def wrapper(*args, **kwargs):
        clock = TimerClock(func, args, kwargs).start()
        result = func(*args, **kwargs)
        clock.stop()
        callback(clock)
        return result
    return wrapper


def timer(func):
    return timer_wrapper_factory(func, print)


def timer_cb(callback):
    def decorator(func):
        return timer_wrapper_factory(func, callback)
    return decorator
