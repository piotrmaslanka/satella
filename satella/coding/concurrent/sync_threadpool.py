import time
from concurrent.futures import wait, ThreadPoolExecutor

from .atomic import AtomicNumber
from .thread import Condition


def sync_threadpool(tpe: ThreadPoolExecutor) -> None:
    """
    Make sure that every thread of given thread pool executor is done processing
    jobs scheduled until this moment.

    Make sure that other tasks do not submit anything to this thread pool executor.

    :param tpe: thread pool executor to sync
    """
    assert isinstance(tpe, ThreadPoolExecutor), 'Must be a ThreadPoolExecutor!'

    workers = tpe._max_workers
    atm_n = AtomicNumber(workers)
    cond = Condition()

    def decrease_atm():
        nonlocal atm_n
        atm_n -= 1
        cond.wait()

    futures = [tpe.submit(decrease_atm) for _ in range(workers)]

    # wait for all currently scheduled jobs to be picked up
    while tpe._work_queue.qsize() > 0:
        time.sleep(0.5)

    atm_n.wait_until_equal(0)
    cond.notify_all()
    wait(futures)

