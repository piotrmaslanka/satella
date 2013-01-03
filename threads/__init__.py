class BaseThread(Thread):
    """Thread with internal termination flag"""
    def __init__(self, *args, **kwargs):
        self._terminating = False
        Thread.__init__(self, *args, **kwargs)

    def terminate(self):
        """Sets internal termination flag"""
        self._terminating = True