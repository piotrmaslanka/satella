import concurrent
import typing as tp
from concurrent.futures import Future

from satella.exceptions import WouldWaitMore


class FutureCollection:
    """
    A set of futures sharing a common result, or a common exception.

    This overloads the operator + for making an union of futures. It can be used
    with either instances of :class:`~satella.coding.concurrent.FutureCollection`
    or normal futures.

    Also supports the indexing operator to get n-th future.
    """
    __slots__ = 'futures',

    def __init__(self, futures: tp.Sequence[Future] = ()):
        if not isinstance(futures, list):
            futures = list(futures)
        self.futures = futures

    def __getitem__(self, n: int) -> Future:
        return self.futures[n]

    def __add__(self, other: tp.Union['FutureCollection', Future, tp.Sequence[Future]]):
        if isinstance(other, FutureCollection):
            return FutureCollection(self.futures + other.futures)
        elif isinstance(other, tp.Sequence):
            return FutureCollection(self.futures + list(other))
        else:
            fc = self.futures[:]
            fc.append(other)
            return FutureCollection(fc)

    def add_done_callback(self, callback, only_one: bool = False) -> None:
        """
        Add a callback to a Future to be called on it's completion.

        By default, this will add the callback to all futures.

        :param callback: callback that takes the completed Future as argument
        :param only_one: callback will be added only to a single Future. False by default
        :raises IndexError: only_one was given and no Futures in collection!
        """
        if only_one:
            self.futures[0].add_done_callback(callback)
        else:
            for future in self.futures:
                future.add_done_callback(callback)

    def set_running_or_notify_cancel(self) -> bool:
        """
        Call :code:`set_running_or_notify_cancel` on the futures

        This will return True if at least one future was not cancelled
        """
        starting = False
        for future in self.futures:
            starting = starting or future.set_running_or_notify_cancel()
        return starting

    def __iadd__(self, other: tp.Union['FutureCollection', Future, tp.Sequence[Future]]):
        if isinstance(other, FutureCollection):
            self.futures.extend(other.futures)
            return self
        elif isinstance(other, tp.Sequence):
            self.futures.extend(other)
            return self
        else:
            self.futures.append(other)
            return self

    def add(self, future: Future) -> 'FutureCollection':
        """
        Add a future

        :param future: a Future to add
        :return: self
        """
        self.futures.append(future)
        return self

    def set_result(self, result) -> None:
        """
        Set a result for all futures

        :param result: result to set
        """
        for future in self.futures:
            future.set_result(result)

    def set_exception(self, exc) -> None:
        """
        Set an exception for all futures

        :param exc: exception instance to set
        """
        for future in self.futures:
            future.set_exception(exc)

    def result(self, timeout: tp.Optional[float] = None) -> list:
        """
        Return the result of all futures, as a list.

        This will block until the results are available.

        :param timeout: a timeout in seconds for a single result. Default value None means
            wait as long as necessary
        :return: list containing results of all futures
        :raises WouldWaitMore: timeout while waiting for result
        """
        try:
            return [fut.result(timeout) for fut in self.futures]
        except concurrent.futures.TimeoutError:
            raise WouldWaitMore('timeout waiting for the result')

    def exception(self, timeout: tp.Optional[float] = None) -> tp.Optional[Exception]:
        """
        Return first exception raised by any of the futures

        This will block until the results are available.
        This call proceeding does not mean that results for all are available, since
        this will return the first exception encountered!

        :param timeout: a timeout in seconds for a single result. Default value None means
            wait as long as necessary
        :return: the first exception, or None if there were no exceptions
        :raises WouldWaitMore: timeout while waiting for result
        """
        try:
            for fut in self.futures:
                e = fut.exception(timeout)
                if e is not None:
                    return e
            return None
        except concurrent.futures.TimeoutError:
            raise WouldWaitMore('timeout waiting for the result')

    def cancel(self) -> bool:
        """
        Cancel all futures

        :return: True if all sections were cancelled
        """
        all_cancelled = True
        for future in self.futures:
            all_cancelled = all_cancelled and future.cancel()
        return all_cancelled

