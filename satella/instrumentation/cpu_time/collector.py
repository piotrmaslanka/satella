from __future__ import annotations

import collections
import multiprocessing
import os
import time
import typing as tp

import psutil

from satella.coding import for_argument
from satella.coding.concurrent import SingleStartThread
from satella.coding.decorators import repeat_forever
from satella.coding.transforms import percentile
from satella.time import parse_time_string

DEFAULT_REFRESH_EACH = '10s'
DEFAULT_WINDOW_SECONDS = '10s'

pCPUtimes = collections.namedtuple('pcputimes',
                                   ['user', 'system', 'children_user', 'children_system',
                                    'iowait'], defaults=[0, 0, 0, 0, 0])


class _CPUProfileBuilderThread(SingleStartThread):
    """
    A CPU profile builder thread and a core singleton object to use.

    :param window_seconds: the amount of seconds for which to collect data.
        Generally, this should be the interval during which your system cycles through all of
        its load, eg. if it asks its devices each 5 minutes, the interval should be 300 seconds.
        Or a time string.
    :param refresh_each: time of seconds to sleep between rebuilding of profiles, or a time string.
    """
    thread = None

    def __init__(self, window_seconds: tp.Union[str, int] = DEFAULT_WINDOW_SECONDS,
                 refresh_each: tp.Union[str, int] = DEFAULT_REFRESH_EACH,
                 percentiles_requested: tp.Sequence[float] = (0.9,)):
        super().__init__(name='CPU profile builder', daemon=True)
        self.window_size = int(parse_time_string(window_seconds))
        self.refresh_each = parse_time_string(refresh_each)
        self.data = []
        self.process = psutil.Process(os.getpid())
        self.percentiles_requested = list(percentiles_requested)
        self.percentile_values = []
        self.percentiles_regenerated = False
        self.started = False
        self.own_load_average = collections.deque()  # typing: tuple[float, pCPUtimes]

    @staticmethod
    def get_instance():
        """Access instances of this thread in this way ONLY!"""
        if _CPUProfileBuilderThread.thread is None:
            _CPUProfileBuilderThread.thread = _CPUProfileBuilderThread()
            _CPUProfileBuilderThread.thread.start()
        return _CPUProfileBuilderThread.thread

    def save_load(self, times: pCPUtimes) -> None:
        while len(self.own_load_average) > 3 and \
                self.own_load_average[0][0] < self.own_load_average[-1][0] - self.window_size:
            self.own_load_average.popleft()
        tpl = time.monotonic(), times
        self.own_load_average.append(tpl)

    def get_own_cpu_usage(self) -> tp.Optional[pCPUtimes]:
        """
        Return own CPU usage.

        :return: None if data not yet ready, or a PCPUtimes namedtuple
        """
        if len(self.own_load_average) < 2:
            return None
        time_p, times_v = self.own_load_average[-2]
        time_c, times_c = self.own_load_average[-1]
        difference = time_c - time_p
        if difference == 0:
            return None
        tuple_build = {}
        for field in times_v._fields:  # pylint: disable=protected-access
            tuple_build[field] = (getattr(times_c, field) - getattr(times_v, field)) / difference
        return pCPUtimes(**tuple_build)

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

    def _recalculate(self) -> None:
        """Takes as long as window size"""
        data = []
        calculate_occupancy_factor()  # as first values tend to be a bit wonky
        for _ in range(int(self.window_size)):
            time.sleep(1)
            data.append(calculate_occupancy_factor())
        percentiles = []
        data.sort()
        for percent in self.percentiles_requested:
            percentiles.append(percentile(data, percent))
        self.percentile_values = percentiles
        self.percentiles_regenerated = True
        self.data = data

    @repeat_forever
    def run(self):
        self._recalculate()
        self.save_load(self.process.cpu_times())
        time.sleep(self.refresh_each)


class CPUTimeManager:
    @staticmethod
    def percentile(percent: float) -> float:
        """
        Return given percentile of current CPU time's profile
        :param percent: float between 0 and 1
        :return: the value of the percentile
        """
        return _CPUProfileBuilderThread.get_instance().percentile(percent)

    @staticmethod
    def set_window_size(window_size: float) -> None:
        """
        Set the time that should be observed in order to build an execution profile.

        :param window_size: time, in seconds
        """
        _CPUProfileBuilderThread.get_instance().window_size = window_size

    @staticmethod
    def set_refresh_each(refresh: tp.Union[str, float, int]) -> None:
        """Change the refresh interval for the CPU usage collection thread"""

        _CPUProfileBuilderThread.get_instance().refresh_each = parse_time_string(refresh)


@for_argument(parse_time_string)
def sleep_cpu_aware(seconds: tp.Union[str, float], of_below: tp.Optional[float] = None,
                    of_above: tp.Optional[float] = None,
                    check_each: float = 1) -> bool:
    """
    Sleep for specified number of seconds.

    Quit earlier if the occupancy factor goes below of_below or above of_above
    :param seconds: time to sleep in seconds, or a time string
    :param of_below: occupancy factor below which the sleep will return
    :param of_above: occupancy factor above which the sleep will return
    :param check_each: amount of seconds to sleep at once
    :return: whether was awoken due to CPU time condition
    """
    v = False
    if of_below is None and of_above is None:
        time.sleep(seconds)
    else:
        calculate_occupancy_factor()  # prime the counter
        while seconds > 0:
            time_to_sleep = min(seconds, check_each)
            time.sleep(time_to_sleep)
            of = calculate_occupancy_factor()

            if of_above is not None:
                if of > of_above:
                    v = True
                    break
            if of_below is not None:
                if of < of_below:
                    v = True
                    break
            seconds -= time_to_sleep
            if seconds <= 0:
                break
    return v


previous_cf = None  # type: float
previous_timestamp = None  # type: float


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
    of = (occupation_factor - previous_cf) / delta
    previous_cf = occupation_factor
    previous_timestamp = cur_time
    return of


def calculate_occupancy_factor() -> float:
    """
    Get the average load between now and the time it was last called as a float,
    where 0.0 is LA=0 and 1.0 is LA=max_cores.

    This will be the average between now and the time it was last called.

    .. warning:: This in rare cases (being called the first or the second time) may block for
                 up to 0.1 seconds

    :return: a float between 0 and 1 telling you how occupied CPU-wise is your system.
    """
    _CPUProfileBuilderThread.get_instance()
    c = _calculate_occupancy_factor()
    while c is None:
        time.sleep(0.1)
        c = _calculate_occupancy_factor()
    return c


def get_own_cpu_usage() -> tp.Optional[pCPUtimes]:
    """
    Return own CPU usage (this process only)

    :return: None if data not ready (just try again in some time), or a a namedtuple of (user, system, children_user,
        children_system, iowait) divided by number of seconds that passed since the last measure. The result is divided
        by passed time, so a 1 means 100% during the time, and 0.5 means exactly 50% of the CPU used.
    """
    return _CPUProfileBuilderThread.get_instance().get_own_cpu_usage()
