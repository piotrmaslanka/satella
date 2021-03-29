import threading
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

    This also implements iteration (it will return all the threads in the collection) and
    length check.
    """

    __slots__ = ('threads', )

    def __len__(self):
        return len(self.threads)

    def __iter__(self):
        return iter(self.threads)

    @classmethod
    def get_currently_running(cls, include_main_thread: bool = True) -> 'ThreadCollection':
        """
        Get all currently running threads as thread collection

        :param include_main_thread: whether to include the main thread

        :return: a thread collection representing all currently running threads
        """
        result = []
        for thread in threading.enumerate():
            # noinspection PyProtectedMember
            if not include_main_thread and isinstance(thread, threading._MainThread):
                continue
            result.append(thread)
        return ThreadCollection(result)

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

    def __init__(self, threads: tp.Sequence[Thread]):
        self.threads = list(threads)

    def append(self, thread: Thread) -> 'ThreadCollection':
        """
        Alias for :meth:`~satella.coding.concurrent.ThreadCollection.add`

        :param thread: thread to add
        :returns: this thread collection instance
        """
        self.add(thread)
        return self

    def add(self, thread: Thread) -> 'ThreadCollection':
        """
        Add a thread to the collection

        :param thread: thread to add
        :returns: this thread collection instance
        """
        self.threads.append(thread)
        return self

    def start(self) -> 'ThreadCollection':
        """
        Start all threads

        :returns: this thread collection instance
        """
        for thread in self.threads:
            thread.start()
        return self

    def terminate(self, *args, **kwargs) -> 'ThreadCollection':
        """
        Call terminate() on all threads that have this method

        :returns: this thread collection instance
        """
        for thread in self.threads:
            try:
                thread.terminate(*args, **kwargs)
            except AttributeError:
                pass
        return self

    def join(self) -> 'ThreadCollection':
        """
        Join all threads

        :returns: this thread collection instance
        """
        for thread in self.threads:
            thread.join()
        return self

    def is_alive(self) -> bool:
        """
        Is at least one thread alive?
        """
        return any(thread.is_alive() for thread in self.threads)
