import ctypes

import platform
import threading
import typing as tp
from threading import Condition as PythonCondition

from satella.time import measure
from ...exceptions import ResourceLocked, WouldWaitMore


class Condition(PythonCondition):
    """
    A wrapper to faciliate easier usage of Pythons' threading.Condition.

    There's no need to acquire the underlying lock, as wait/notify/notify_all do it for you.

    This happens to sorta not work on PyPy. Use at your own peril. You have been warned.
    """

    def wait(self, timeout: tp.Optional[float] = None):
        """
        Wait for condition to become true.

        :param timeout: timeout to wait. None is default and means infinity
        :raises ResourceLocked: unable to acquire the underlying lock within specified timeout.
        :raises WouldWaitMore: wait's timeout has expired
        """
        with measure() as measurement:
            if timeout is None:
                self.acquire()
            else:
                if not self.acquire(timeout=timeout):
                    raise ResourceLocked('internal lock locked')

            try:
                if timeout is None:
                    super().wait()
                else:
                    if not super().wait(timeout=timeout - measurement()):
                        raise WouldWaitMore('wait was not notified')
            finally:
                self.release()

    def notify_all(self) -> None:
        """
        Notify all threads waiting on this Condition
        """
        with self._lock:
            super().notify_all()

    def notify(self, n: int = 1):
        """
        Notify n threads waiting on this Condition

        :param n: amount of threads to notify
        """
        with self._lock:
            super().notify(n=n)


class TerminableThread(threading.Thread):
    """
    Class that will execute something in a loop unless terminated. Use like:

    >>> class MeGrimlock(TerminableThread):
    >>>     def loop(self):
    >>>         ... do your operations ..
    >>> a = MeGrimlock()
    >>> a.start()
    >>> a.terminate().join()

    Flag whether to terminate is stored in **self._terminating**.

    If you decide to override run(), you got to check periodically for **self._terminating** to
    become true.
    If you decide to use the loop/cleanup interface, you don't need to do so.

    You may also use it as a context manager. Entering the context will start the thread, and
    exiting it will .terminate().join() it, in the following way:

    >>> a = MeGrimlock()
    >>> with a:
    >>>     ...
    >>> self.assertFalse(a.is_alive())
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._terminating = False  # type: bool

    def loop(self) -> None:
        """
        Run one iteration of the loop. Meant to be overrided. You do not need to override it
        if you decide to override run() through.

        This should block for as long as a single check will take, as termination checks take place
        between calls.
        """

    def run(self) -> None:
        """
        Calls self.loop() indefinitely, until terminating condition is met
        """
        while not self._terminating:
            self.loop()
        self.cleanup()

    def cleanup(self):
        """
        Called after thread non-forced termination, in the thread's context.

        The default implementation does nothing.
        """

    def __enter__(self):
        """Returns self"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate().join()
        return False

    def terminate(self, force: bool = False) -> 'TerminableThread':
        """
        Signal this thread to terminate.

        Forcing, if requested, will be done by injecting a SystemExit exception into target
        thread, so the thread must acquire GIL. For example, following would not be interruptable:

        >>> time.sleep(1000000)

        Note that calling force=True on PyPy won't work, and NotImplementedError will be raised
        instead.

        :param force: Whether to force a quit
        :return: self
        :raises RuntimeError: when something goes wrong with the underlying Python machinery
        :raises NotImplementedError: force=True was used on PyPy
        """
        self._terminating = True
        if force:
            if platform.python_implementation() == 'PyPy':
                raise NotImplementedError('force=True was made on PyPy')
            ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self._ident),
                                                             ctypes.py_object(SystemExit))
            if ret == 0:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self._ident), 0)
                raise RuntimeError('Zero threads killed!')
            elif ret > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self._ident), 0)
                raise RuntimeError('Multiple threads killed!')

        return self
