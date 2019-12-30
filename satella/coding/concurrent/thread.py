import threading
import ctypes


class TerminableThread(threading.Thread):
    """
    Class that will execute something in a loop unless terminated. Use like:

    >>> class MeGrimlock(TerminableThread):
    >>>     def loop(self):
    >>>         ... do your operations ..
    >>> a = MeGrimlock()
    >>> a.start()
    >>> a.terminate().join()

    Flag whether to terminate is stored in self._terminating
    """
    def __init__(self):
        super().__init__()
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

    def terminate(self, force: bool = False) -> 'TerminableThread':
        """
        Signal this thread to terminate.

        Forcing, if requested, will be done by injecting a SystemExit exception into target
        thread, so the thread must acquire GIL. For example, following would not be interruptable:

        >>> time.sleep(1000000)

        :param force: Whether to force a quit
        :raises ValueError: force was set to True, and the thread's TID could not be obtained
        """
        self._terminating = True
        if force:
            found = False
            for tid, tobj in threading._active.items():
                if tobj is self:
                    found = True
                    target_tid = tid
                    break

            if not found:
                raise ValueError('Thread ID for thread %s was not found' % (self, ))

            ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(target_tid, ctypes.py_object(SystemExit))
            if ret == 0:
                raise ValueError('Invalid thread ID %s obtained for %s' % (target_tid, self))

        return self
