from typing import Callable
from threading import Thread
import time

from src.common.utils import synchronized


class Heartbeat:
    def __init__(self, callback: Callable[[], None], interval_sec: float):
        self._callback = callback
        self._interval_sec = interval_sec
        self._thread = Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    @synchronized
    def send(self) -> None:
        self._callback()

    def _run(self) -> None:
        while True:
            self.send()
            time.sleep(self._interval_sec)