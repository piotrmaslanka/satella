from concurrent.futures import Executor
from .futures import WrappingFuture, Future


class ExecutorWrapper(Executor):
    """
    A wrapping for Python executors to return Satella futures instead of standard Python ones.
    """
    __slots__ = ('executor', )

    def __init__(self, executor: Executor):
        self.executor = executor

    def submit(self, fn, *args, **kwargs) -> Future:
        fut = self.executor.submit(fn, *args, **kwargs)
        return WrappingFuture(fut)

    def map(self, fn, *iterables, timeout=None, chunksize=1):
        yield from self.executor.map(fn, *iterables, timeout=timeout, chunksize=chunksize)

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

    def __enter__(self):
        return self.executor.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown(wait=True)
        return False
