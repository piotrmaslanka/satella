from threading import Thread


class TerminableThread(Thread):
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
        pass

    def run(self) -> None:
        while not self._terminating:
            self.loop()

    def terminate(self) -> 'TerminableThread':
        self._terminating = True
        return self
