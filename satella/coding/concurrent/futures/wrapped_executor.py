from concurrent.futures import Executor

from .futures import Future, wrap_if


class ExecutorWrapper(Executor):
    """
    A wrapping for Python executors to return Satella futures instead of standard Python ones.
    """

    def __init__(self, executor: Executor):
        self.executor = executor

    def submit(self, fn, *args, **kwargs) -> Future:
        return wrap_if(self.executor.submit(fn, *args, **kwargs))

    def shutdown(self, wait=True):
        """Clean-up the resources associated with the Executor.

        It is safe to call this method several times. Otherwise, no other
        methods can be called after this one.

        Args:
            wait: If True then shutdown will not return until all running
                futures have finished executing and the resources used by the
                executor have been reclaimed.
        """
        return self.executor.shutdown(wait=wait)
