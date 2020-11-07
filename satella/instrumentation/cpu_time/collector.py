import typing as tp
import threading
import multiprocessing
import time

import psutil

from satella.coding.structures import Singleton
from satella.coding.transforms import percentile


@Singleton
class CPUProfileBuilderThread(threading.Thread):
    """
    A CPU profile builder thread and a core singleton object to use.

    :param window_seconds: the amount of seconds for which to collect data
    :param refresh_each: time of seconds to sleep between rebuilding of profiles
    """
    def __init__(self, window_seconds: int = 300, refresh_each: int = 1800,
                 percentiles_requested: tp.Sequence[float] = (0.9, )):
        super().__init__(name='CPU profile builder', daemon=True)
        self.window_size = window_seconds
        self.refresh_each = refresh_each
        self.data = []
        self.percentiles_requested = list(percentiles_requested)
        self.percentile_values = []
        self.percentiles_regenerated = False
        self.start()

    def request_percentile(self, percent: float) -> None:
        if percent not in self.percentiles_requested:
            self.percentiles_requested.append(percent)
            self.percentiles_regenerated = False

    def percentile(self, percent: float) -> float:
        if not self.data:
            return 0
        if percent in self.percentiles_requested and self.percentiles_regenerated:
            return self.percentile_values[self.percentiles_requested.index(percent)]
        else:
            return percentile(self.data, percent)

    def is_done(self) -> bool:
        return bool(self.data)

    def recalculate(self) -> None:
        data = []
        calculate_occupancy_factor()    # as first values tend to be a bit wonky
        for _ in range(self.window_size):
            time.sleep(1)
            data.append(calculate_occupancy_factor())
        percentiles = []
        data.sort()
        for percent in self.percentiles_requested:
            percentiles.append(percentile(data, percent))
        self.percentile_values = percentiles
        self.percentiles_regenerated = True
        self.data = data

    def run(self):
        while True:
            time.sleep(self.refresh_each)
            self.recalculate()


class CPUTimeManager:
    @staticmethod
    def percentile(percent: float) -> float:
        """
        Return given percentile of current CPU time's profile
        :param percent: float between 0 and 1
        :return: the value of the percentile
        """
        cp = CPUProfileBuilderThread()
        return cp.percentile(percent)

    @staticmethod
    def set_window_size(window_size: float) -> None:
        """
        Set the time that should be observed in order to build an execution profile.

        :param window_size: time, in seconds
        """
        cp = CPUProfileBuilderThread()
        cp.window_size = window_size


def sleep_cpu_aware(seconds: float, of_below: tp.Optional[float] = None,
                    of_above: tp.Optional[float] = None,
                    check_each: float = 1) -> bool:
    """
    Sleep for specified number of seconds.

    Quit earlier if the occupancy factor goes below of_below or above of_above
    :param seconds: time to sleep
    :param of_below: occupancy factor below which the sleep will return
    :param of_above: occupancy factor above which the sleep will return
    :param check_each: amount of seconds to sleep at once
    :return: whether was awoken due to CPU time condition
    """
    if of_below is None and of_above is None:
        time.sleep(seconds)
        return False
    calculate_occupancy_factor()        # prime the counter
    while seconds > 0:
        time_to_sleep = min(seconds, check_each)
        time.sleep(time_to_sleep)
        of = calculate_occupancy_factor()

        if of_above is not None:
            if of > of_above:
                return True
        if of_below is not None:
            if of < of_below:
                return True
        seconds -= time_to_sleep
        if seconds <= 0:
            return False
    return False


previous_cf = None           # type: float
previous_timestamp = None    # type: float


def _calculate_occupancy_factor() -> float:
    c = psutil.cpu_times()
    try:
        try:
            try:
                used = c.user + c.nice + c.system + c.irq + c.softirq + c.steal + c.guest + c.guest_nice
            except AttributeError:
                # Linux?
                used = c.user + c.nice + c.system + c.irq + c.softirq
        except AttributeError:
            # UNIX ?
            used = c.user + c.nice + c.system
    except AttributeError:
        # windows?
        used = c.user + c.system + c.interrupt + c.dpc
    cur_time = time.monotonic()
    occupation_factor = used / multiprocessing.cpu_count()
    global previous_timestamp, previous_cf
    if previous_timestamp is None:
        previous_cf = occupation_factor
        previous_timestamp = cur_time
        return
    delta = cur_time - previous_timestamp
    if delta == 0:
        return
    of = (occupation_factor - previous_cf)/delta
    previous_cf = occupation_factor
    previous_timestamp = cur_time
    return of


def calculate_occupancy_factor() -> float:
    """
    IMPORTANT!

    This will be the average between now and the time it was last called.

    This in rare cases (being called the first or the second time) may block for up to 0.1 seconds

    :return: a float between 0 and 1 telling you how occupied CPU-wise is your system.
    """
    c = _calculate_occupancy_factor()
    while c is None:
        time.sleep(0.1)
        c = _calculate_occupancy_factor()
    return c

