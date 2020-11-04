from abc import abstractmethod, ABCMeta

from satella.coding.concurrent import IntervalTerminableThread
from satella.cpu_time import sleep_except
from satella.cpu_time.collector import CPUProfileBuilderThread
from satella.time import measure

CHECK_INTERVAL = 2


class CPUTimeAwareIntervalTerminableThread(IntervalTerminableThread, metaclass=ABCMeta):
    """
    An IntervalTerminableThread that can call the loop a bit faster than usual,
    based of current CPU time metrics.

    :param seconds: time that a single looping through should take. This will
        include the time spent on calling .loop(), the rest of this time will
        be spent safe_sleep()ing.
    :param max_sooner: amount of seconds that is ok to call this earlier
    :param percentile: percentile that CPU usage has to fall below to call it earlier.
    """

    def __init__(self, seconds: float, max_sooner: float, percentile: float, *args, **kwargs):
        self.seconds = seconds
        self.max_sooner = max_sooner
        cp_bt = CPUProfileBuilderThread()
        cp_bt.request_percentile(percentile)
        self.percentile = percentile
        super().__init__(seconds, *args, **kwargs)

    @abstractmethod
    def loop(self) -> None:
        """
        Override me!

        If True is returned, the thread will not sleep and .loop() will be executed
        once more.
        """

    def run(self):
        self.prepare()
        while not self._terminating:
            with measure() as measurement:
                v = self.loop()
            if measurement() > self.seconds:
                continue
            seconds_to_wait = self.seconds - measurement()
            while seconds_to_wait > 0:
                if seconds_to_wait > self.max_sooner:
                    self.safe_sleep(seconds_to_wait - self.max_sooner)
                    seconds_to_wait -= self.max_sooner
                if seconds_to_wait <= 0:
                    continue
                cp_bt = CPUProfileBuilderThread()
                perc_val = cp_bt.percentile(self.percentile)

                while seconds_to_wait > 0:
                    time_to_sleep = min(CHECK_INTERVAL, seconds_to_wait)
                    if sleep_except(time_to_sleep, perc_val) or self.terminating:
                        seconds_to_wait = 0
                        break
                    seconds_to_wait -= time_to_sleep
        self.cleanup()
