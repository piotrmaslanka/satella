import typing as tp
import time
from concurrent.futures import wait, ThreadPoolExecutor

from satella.coding.concurrent.atomic import AtomicNumber
from satella.coding.concurrent.futures import ExecutorWrapper
from satella.coding.concurrent.thread import Condition
from satella.exceptions import WouldWaitMore
from satella.time.measure import measure


def _while_sync_threadpool(tpe, max_wait, measurement, futures):
    while tpe._work_queue.qsize() > 0:      # pylint: disable=protected-access
        if max_wait is not None:
            if measurement() > max_wait:
                for future in futures:
                    future.cancel()
                raise WouldWaitMore('timeout exceeded')
        time.sleep(0.5)


def _max_wait_atm_n(measurement, max_wait, atm_n):
    while measurement() < max_wait:
        try:
            atm_n.wait_until_equal(0, 1)
            return
        except WouldWaitMore:
            continue
    raise WouldWaitMore('timeout exceeded')


def sync_threadpool(tpe: tp.Union[ExecutorWrapper, ThreadPoolExecutor],
                    max_wait: tp.Optional[float] = None) -> None:
    """
    Make sure that every thread of given thread pool executor is done processing
    jobs scheduled until this moment.

    Make sure that other tasks do not submit anything to this thread pool executor.

    :param tpe: thread pool executor to sync. Can be also a ExecutorWrapper.
    :param max_wait: maximum time to wait. Default, None, means wait forever
    :raises WouldWaitMore: timeout exceeded. Raised only when max_wait is not None.
    """
    if isinstance(tpe, ExecutorWrapper):
        return sync_threadpool(tpe.executor, max_wait=max_wait)

    assert isinstance(tpe, ThreadPoolExecutor), 'Must be a ThreadPoolExecutor!'

    with measure(timeout=max_wait) as measurement:
        workers = tpe._max_workers      # pylint: disable=protected-access
        atm_n = AtomicNumber(workers)
        cond = Condition()

        def decrease_atm():
            nonlocal atm_n
            atm_n -= 1
            cond.wait()

        futures = [tpe.submit(decrease_atm) for _ in range(workers)]

        # wait for all currently scheduled jobs to be picked up
        _while_sync_threadpool(tpe, max_wait, measurement, futures)

        if max_wait is None:
            atm_n.wait_until_equal(0)
        else:
            _max_wait_atm_n(measurement, max_wait, atm_n)
        cond.notify_all()
        wait(futures)
