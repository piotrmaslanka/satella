import typing as tp
from threading import Thread


class ThreadCollection:
    """
    A collection of threads.

    Create like:

    >>> class MyThread(Thread):
    >>>     def __init__(self, a):
    >>>         ...
    >>> tc = ThreadCollection.from_class(MyThread, [2, 4, 5])
    >>> tc.start()
    >>> tc.terminate()
    >>> tc.join()
    """

    __slots__ = ('threads', )

    @classmethod
    def from_class(cls, cls_to_use, iteratable) -> 'ThreadCollection':
        """
        Build a thread collection

        :param cls_to_use: class to instantiate with
        :param iteratable: an iterable with the sole argument to this class
        """
        return ThreadCollection([cls_to_use(it) for it in iteratable])

    def __init__(self, threads: tp.List[Thread]):
        self.threads = threads

    def start(self):
        """
        Start all threads
        """
        for thread in self.threads:
            thread.start()

    def terminate(self, *args, **kwargs):
        """
        Call terminate() on all threads that have this method
        """
        for thread in self.threads:
            try:
                thread.terminate(*args, **kwargs)
            except AttributeError:
                pass

    def join(self):
        """Join all threads"""
        for thread in self.threads:
            thread.join()

    def is_alive(self):
        """
        Is at least one thread alive?
        """
        return any(thread.is_alive() for thread in self.threads)
