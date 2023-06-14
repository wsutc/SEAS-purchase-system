import time


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Timer:
    def __init__(self, text="Elapsed time: {:0.4f} seconds", logger=print):
        self._start_time = None
        self.text = text
        self.logger = logger

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError("Timer is running; use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self):
        """Stop the timer and report the elapsed time"""
        if self._start_time is None:
            raise TimerError("Timer is not running; use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None

        if self.logger:
            self.logger(self.text.format(elapsed_time))

        return elapsed_time
