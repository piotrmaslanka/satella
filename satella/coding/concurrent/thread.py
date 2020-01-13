import ctypes
import logging
import platform
import threading

logger = logging.getLogger(__name__)


class TerminableThread(threading.Thread):
    """
    Class that will execute something in a loop unless terminated. Use like:

    >>> class MeGrimlock(TerminableThread):
    >>>     def loop(self):
    >>>         ... do your operations ..
    >>> a = MeGrimlock()
    >>> a.start()
    >>> a.terminate().join()

    Flag whether to terminate is stored in self._terminating.

    If you decide to override run(), you got to check periodically for self._terminating to become true.
    If you decide to use the loop/cleanup interface, you don't need to do so.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._terminating = False

    def loop(self) -> None:
        """
        Run one iteration of the loop. Meant to be overrided.

        This should block for as long as a single check will take, as termination checks take place
        between calls.
        """
        raise NotImplementedError('Override me!')

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

    def terminate(self, force: bool = False) -> 'TerminableThread':
        """
        Signal this thread to terminate.

        Forcing, if requested, will be done by injecting a SystemExit exception into target
        thread, so the thread must acquire GIL. For example, following would not be interruptable:

        Note that calling force=True on PyPy won't work, and RuntimeError will be raised instead.

        >>> time.sleep(1000000)

        :param force: Whether to force a quit
        :return: self
        :raises RuntimeError: when something goes wrong with the underlying Python machinery
        """
        self._terminating = True
        if force:
            if platform.python_implementation() == 'PyPy':
                raise RuntimeError('force=True was made on PyPy')
            ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self._ident),
                                                             ctypes.py_object(SystemExit))
            if ret == 0:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self._ident), 0)
                raise RuntimeError('Multiple threads killed!')
            elif ret > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self._ident), 0)
                raise RuntimeError('Multiple threads killed!')

        return self
