from datetime import datetime
from datetime import timedelta

__all__ = ('StopWatch',)


class StopWatch:
    def __init__(self):
        self.start_time = None
        self.is_counting = False

        self.pause_start = None
        self.is_paused = False

        self.resume = self.unpause
        self.reset = self.stop

    def start(self):
        """Start the stopwatch"""

        self.start_time = datetime.now()
        self.is_counting = True

    def stop(self) -> timedelta:
        """Stop the stopwatch.

        Returns
        -------
            time: :class:`datetime.timedelta`
                The time on the stopwatch before being stopped.
        """

        if self.is_paused:
            self.unpause()
        time = self.get_time()
        self.start_time = None
        self.is_counting = False
        return time

    def pause(self) -> None:
        """Pause the stopwatch"""

        if self.is_paused:
            return
        self.pause_start = datetime.now()
        self.is_paused = True

    def unpause(self) -> None:
        """Unpause the stopwatch"""

        if not self.is_paused:
            return
        now = datetime.now()
        self.start_time = self.start_time + (now - self.pause_start)
        self.pause_start = None
        self.is_paused = False

    def get_time(self) -> timedelta:
        """Gets the current time on the stopwatch,

        Returns
        -------
            time: :class:`datetime.timedelta`
                The current time on the stopwatch,
        """

        if not self.is_counting:
            return timedelta(seconds=0)
        now = datetime.now()
        time = now - self.start_time
        if self.is_paused:
            pause_amount = now - self.pause_start
            time = time - pause_amount
        return time
