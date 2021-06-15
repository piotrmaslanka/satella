import time
import typing as tp
from concurrent.futures import wait, ThreadPoolExecutor

from .atomic import AtomicNumber
from .futures import ExecutorWrapper
from .thread import Condition
from ...exceptions import WouldWaitMore
from ...time.measure import measure


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
        # noinspection PyProtectedMember
        workers = tpe._max_workers
        atm_n = AtomicNumber(workers)
        cond = Condition()

        def decrease_atm():
            nonlocal atm_n
            atm_n -= 1
            cond.wait()

        futures = [tpe.submit(decrease_atm) for _ in range(workers)]

        # wait for all currently scheduled jobs to be picked up
        # noinspection PyProtectedMember
        while tpe._work_queue.qsize() > 0:
            if max_wait is not None:
                if measurement() > max_wait:
                    for future in futures:
                        future.cancel()
                    raise WouldWaitMore('timeout exceeded')
            time.sleep(0.5)

        if max_wait is None:
            atm_n.wait_until_equal(0)
        else:
            while measurement() < max_wait:
                try:
                    atm_n.wait_until_equal(0, 1)
                    break
                except WouldWaitMore:
                    continue
            else:
                raise WouldWaitMore('timeout exceeded')
        cond.notify_all()
        wait(futures)
