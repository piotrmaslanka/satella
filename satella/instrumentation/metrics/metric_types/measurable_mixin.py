import inspect
import time
import typing as tp
from concurrent.futures import Future

from satella.coding import wraps
from .base import MetricLevel


class MeasurableMixin:
    """
    Add a .measure() method, useful for HistogramMetric and SummaryMetric
    """
    __slots__ = ()

    def measure_future(self, future: Future, logging_level: MetricLevel = MetricLevel.RUNTIME,
                       value_getter: tp.Callable[[], float] = time.monotonic, **labels):
        """
        A function to measure a difference between some value after the method call
        and before it.

        The value will be taken at the moment this function executes, and the moment the future
        completes (with or without an exception)

        :param future: future that is considered
        :param logging_level: one of RUNTIME or DEBUG
        :param value_getter: a callable that takes no arguments and returns a float, which is
            the value
        :param labels: extra labels to call handle() with
        """
        future.old_value = value_getter()

        def on_future_done(fut: Future):
            self.handle(logging_level, value_getter() - fut.old_value, **labels)

        future.add_done_callback(on_future_done)

    def measure(self, include_exceptions: bool = True,
                logging_level: MetricLevel = MetricLevel.RUNTIME,
                value_getter: tp.Callable[[], float] = time.monotonic, **labels):
        """
        A decorator to measure a difference between some value after the method call
        and before it.

        By default, it will measure the execution time.

        Use like:

        >>> call_time = getMetric('root.metric_name.execution_time', 'summary')
        >>> @call_time.measure()
        >>> def measure_my_execution(args):
        >>>     ...

        If wrapped around p_gen, it will time it from the first element to the last,
        so beware that it will depend on the speed of the consumer.

        It also can be used as a context manager:

        >>> with call_time.measure(logging_level=MetricLevel.DEBUG, label='key'):
        >>>     ...

        :param include_exceptions: whether to include exceptions
        :param logging_level: one of RUNTIME or DEBUG
        :param value_getter: a callable that takes no arguments and returns a float, which is
            the value
        :param labels: extra labels to call handle() with
        """

        class MeasurableMixinInternal:
            def __init__(self, metric_class, include_exceptions, value_getter,
                         logging_level, labels):
                self.metric_class = metric_class
                self.value_getter = value_getter
                self.logging_level = logging_level
                self.include_exceptions = include_exceptions
                self.labels = labels
                self.value = None

            def __call__(self, fun):
                @wraps(fun)
                def inner_normal(*args, **kwargs):
                    start_value = value_getter()
                    excepted = None
                    try:
                        return fun(*args, **kwargs)
                    except Exception as e:
                        excepted = e
                    finally:
                        value_taken = self.value_getter() - start_value
                        if excepted is not None and not self.include_exceptions:
                            raise excepted

                        self.metric_class.handle(logging_level, value_taken, **labels)

                        if excepted is not None:
                            raise excepted

                @wraps(fun)
                def inner_generator(*args, **kwargs):
                    start_value = value_getter()
                    excepted = None
                    try:
                        yield from fun(*args, **kwargs)
                    except Exception as e:
                        excepted = e
                    finally:
                        value_taken = value_getter() - start_value
                        if excepted is not None and not self.include_exceptions:
                            raise excepted

                        self.metric_class.handle(self.logging_level, value_taken, **self.labels)

                        if excepted is not None:
                            raise excepted

                if inspect.isgeneratorfunction(fun):
                    return inner_generator
                else:
                    return inner_normal

            def __enter__(self):
                self.value = self.value_getter()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if not self.include_exceptions and exc_type is not None:
                    return False

                elapsed = self.value_getter() - self.value
                self.metric_class.handle(self.logging_level, elapsed, **self.labels)

                return False

        return MeasurableMixinInternal(self, include_exceptions, value_getter,
                                       logging_level, labels)
