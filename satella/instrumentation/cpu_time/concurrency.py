import typing as tp
from abc import abstractmethod, ABCMeta

from satella.coding.concurrent import IntervalTerminableThread
from satella.time import measure, parse_time_string
from .collector import sleep_cpu_aware, _CPUProfileBuilderThread


class CPUTimeAwareIntervalTerminableThread(IntervalTerminableThread, metaclass=ABCMeta):
    """
    An IntervalTerminableThread that can call the loop a bit faster than usual,
    based of current CPU time metrics.

    :param seconds: time that a single looping through should take. This will
        include the time spent on calling .loop(), the rest of this time will
        be spent safe_sleep()ing.
        Can be alternatively a time string
    :param max_sooner: amount of seconds that is ok to call this earlier.
        Default is 10% seconds.
    :param percentile: percentile that CPU usage has to fall below to call it earlier.
    :param wakeup_interval: amount of seconds to wake up between to check for _terminating status.
        Can be also a time string

    Same concerns for :code:`terminate_on` as in
    :class:`~satella.coding.concurrent.TerminableThread` apply.
    """

    def __init__(self, seconds: tp.Union[str, float], max_sooner: tp.Optional[float] = None,
                 percentile: float = 0.3,
                 wakeup_interval: tp.Union[str, float] = '3s', *args, **kwargs):
        self.seconds = parse_time_string(seconds)
        self.wakeup_interval = parse_time_string(wakeup_interval)
        self.max_sooner = max_sooner or seconds * 0.1
        cp_bt = _CPUProfileBuilderThread.get_instance()
        cp_bt.request_percentile(percentile)
        self.percentile = percentile
        super().__init__(seconds, *args, **kwargs)

    @abstractmethod
    def loop(self) -> None:
        """
        Override me!
        """

    def _execute_measured(self) -> float:
        with measure() as measurement:
            self.loop()
        return measurement()

    def __sleep_waiting_for_cpu(self, how_long: float) -> None:
        cp_bt = _CPUProfileBuilderThread.get_instance()
        per_val = cp_bt.percentile(self.percentile)

        while how_long > 0 and not self._terminating:
            time_to_sleep = min(self.wakeup_interval, how_long)

            if sleep_cpu_aware(time_to_sleep, per_val):
                break
            how_long -= time_to_sleep

    def __sleep(self, how_long: float) -> None:
        if how_long > self.max_sooner:
            if self.safe_sleep(how_long - self.max_sooner):
                return
            how_long = self.max_sooner
        self.__sleep_waiting_for_cpu(how_long)

    def run(self):
        try:
            try:
                self.prepare()
            except Exception as e:
                if self._terminate_on is not None:
                    if isinstance(e, self._terminate_on):
                        self.terminate()
                        return
                raise
            while not self.terminating:
                try:
                    measured = self._execute_measured()
                except Exception as e:
                    if self._terminate_on is not None:
                        if isinstance(e, self._terminate_on):
                            self.terminate()
                            return
                    raise
                seconds_to_wait = self.seconds - measured
                if seconds_to_wait > 0:
                    self.__sleep(seconds_to_wait)
                elif seconds_to_wait < 0:
                    self.on_overrun(measured)
        finally:
            self.cleanup()
