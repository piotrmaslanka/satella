import typing as tp
from concurrent.futures import Future


class FutureCollection:
    """
    A set of futures sharing a common result, or a common exception.

    This overloads the operator + for making an union of futures. It can be used
    with either instances of :class:`~satella.coding.concurrent.FutureCollection`
    or normal futures.
    """
    __slots__ = 'futures',

    def __init__(self, futures: tp.Sequence[Future] = ()):
        if not isinstance(futures, list):
            futures = list(futures)
        self.futures = futures

    def __add__(self, other: tp.Union['FutureCollection', Future, tp.Sequence[Future]]):
        if isinstance(other, FutureCollection):
            return FutureCollection(self.futures + other.futures)
        elif isinstance(other, tp.Sequence):
            return FutureCollection(self.futures + list(other))
        else:
            fc = self.futures[:]
            fc.append(other)
            return FutureCollection(fc)

    def set_running_or_notify_cancel(self, all_futures: bool = True) -> bool:
        """
        Call :code:`set_running_or_notify_cancel` on the futures

        :param all_futures: if default, True then this function will return True if all futures
            have been cancelled else will return if only one future has been cancelled
        """
        if all_futures:
            starting = True
            for future in self.futures:
                starting = starting and future.set_running_or_notify_cancel()
        else:
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

    def result(self) -> list:
        """
        Return the result of all futures, as a list.

        This will block until the results are available.

        :return: list containing results of all futures
        """
        return [fut.result() for fut in self.futures]

    def cancel(self) -> bool:
        """
        Cancel all futures

        :return: True if all sections were cancelled
        """
        all_cancelled = True
        for future in self.futures:
            all_cancelled = all_cancelled and future.cancel()
        return all_cancelled

