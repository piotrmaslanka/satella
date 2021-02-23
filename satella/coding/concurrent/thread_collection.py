import typing as tp
from threading import Thread


class ThreadCollection:
    """
    A collection of threads.

    Create like:

    >>> class MyThread(Thread):
    >>>     def __init__(self, a):
    >>>         ...
    >>> tc = ThreadCollection.from_class(MyThread, [2, 4, 5], daemon=True)
    >>> tc.start()
    >>> tc.terminate()
    >>> tc.join()
    """

    __slots__ = ('threads', )

    @classmethod
    def from_class(cls, cls_to_use, iteratable, **kwargs) -> 'ThreadCollection':
        """
        Build a thread collection

        :param cls_to_use: class to instantiate with
        :param iteratable: an iterable with the sole argument to this class
        """
        return ThreadCollection([cls_to_use(it, **kwargs) for it in iteratable])

    @property
    def daemon(self) -> bool:
        """
        Is any of the threads a daemon?

        Also, when used a setter sets daemon attribute.
        """
        return any(thread.daemon for thread in self.threads)

    @daemon.setter
    def daemon(self, v: bool) -> None:
        for thread in self.threads:
            thread.daemon = v

    def __init__(self, threads: tp.List[Thread]):
        self.threads = threads

    def start(self) -> None:
        """
        Start all threads
        """
        for thread in self.threads:
            thread.start()

    def terminate(self, *args, **kwargs) -> None:
        """
        Call terminate() on all threads that have this method
        """
        for thread in self.threads:
            try:
                thread.terminate(*args, **kwargs)
            except AttributeError:
                pass

    def join(self) -> None:
        """Join all threads"""
        for thread in self.threads:
            thread.join()

    def is_alive(self) -> bool:
        """
        Is at least one thread alive?
        """
        return any(thread.is_alive() for thread in self.threads)
