import atexit
import weakref
from concurrent.futures import _base
from concurrent.futures import thread
from concurrent.futures.thread import ThreadPoolExecutor, BrokenThreadPool, _WorkItem
import typing as tp
import threading

from satella.time import measure

from satella.instrumentation.metrics.metric_types import EmptyMetric, SummaryMetric, HistogramMetric, MetricLevel, \
    CallableMetric
from ..aggregate import AggregateMetric


def _worker(executor_reference, work_queue, initializer, initargs):
    if initializer is not None:
        try:
            initializer(*initargs)
        except BaseException:
            _base.LOGGER.critical('Exception in initializer:', exc_info=True)
            executor = executor_reference()
            if executor is not None:
                executor._initializer_failed()
            return
    try:
        while True:
            work_item = work_queue.get(block=True)
            if work_item is not None:
                # Measure the time spent in waiting
                executor = executor_reference()
                work_item.measure.stop()
                executor.waiting_time_metric.handle(executor.metric_level, work_item.measure())
                del executor

                with measure() as measurement:
                    work_item.run()

                executor = executor_reference()
                executor.executing_time_metric.handle(executor.metric_level, measurement())
                # Delete references to object. See issue16284
                del work_item

                # attempt to increment idle count

                if executor is not None:
                    executor._idle_semaphore.release()
                del executor
                continue

            executor = executor_reference()
            # Exit if:
            #   - The interpreter is shutting down OR
            #   - The executor that owns the worker has been collected OR
            #   - The executor that owns the worker has been shutdown.
            if thread._shutdown or executor is None or executor._shutdown:
                # Flag the executor as shutting down as early as possible if it
                # is not gc-ed yet.
                if executor is not None:
                    executor._shutdown = True
                # Notice other workers
                work_queue.put(None)
                return
            del executor
    except BaseException:
        _base.LOGGER.critical('Exception in worker', exc_info=True)


class MetrifiedThreadPoolExecutor(ThreadPoolExecutor):
    """
    A thread pool executor that provides execution statistics as metrics.

    :param time_spent_waiting: a metric (can be aggregate) to which times spent waiting in the queue will be deposited
    :param time_spent_executing: a metric (can be aggregate) to which times spent executing will be deposited
    :param waiting_tasks: a fresh CallableMetric that will be patched to yield the number of currently waiting tasks
    :param metric_level: a level with which to log to these two metrics
    """

    def __init__(self, max_workers=None, thread_name_prefix='',
                 initializer=None, initargs=(),
                 time_spent_waiting=None,
                 time_spent_executing=None,
                 waiting_tasks: tp.Optional[CallableMetric] = None,
                 metric_level: MetricLevel = MetricLevel.RUNTIME):
        super().__init__(max_workers, thread_name_prefix, initializer, initargs)
        self.waiting_time_metric = time_spent_waiting or EmptyMetric()
        self.executing_time_metric = time_spent_executing or EmptyMetric()
        self.metric_level = metric_level
        if waiting_tasks is not None:
            waiting_tasks.callable = lambda: self._work_queue.qsize()

    def submit(*args, **kwargs):
        if len(args) >= 2:
            self, fn, *args = args
        elif not args:
            raise TypeError("descriptor 'submit' of 'ThreadPoolExecutor' object "
                            "needs an argument")
        elif 'fn' in kwargs:
            fn = kwargs.pop('fn')
            self, *args = args
            import warnings
            warnings.warn("Passing 'fn' as keyword argument is deprecated",
                          DeprecationWarning, stacklevel=2)
        else:
            raise TypeError('submit expected at least 1 positional argument, '
                            'got %d' % (len(args)-1))

        with self._shutdown_lock:
            if self._broken:
                raise BrokenThreadPool(self._broken)

            if self._shutdown:
                raise RuntimeError('cannot schedule new futures after shutdown')
            if thread._shutdown:
                raise RuntimeError('cannot schedule new futures after '
                                   'interpreter shutdown')

            f = _base.Future()
            w = _WorkItem(f, fn, args, kwargs)
            w.measure = measure()
            self._work_queue.put(w)
            self._adjust_thread_count()
            return f
