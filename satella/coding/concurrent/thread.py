import ctypes
import platform
import threading
import time
import typing as tp
import warnings
from abc import ABCMeta, abstractmethod
from concurrent.futures import Future
from threading import Condition as PythonCondition

from satella.coding.decorators import wraps
from satella.time import measure, parse_time_string
from ..typing import ExceptionList
from ...exceptions import ResourceLocked, WouldWaitMore


def call_in_separate_thread(*t_args, delay: float = 0, **t_kwargs):
    """
    Decorator to mark given routine as callable in a separate thread.

    The decorated routine will return a Future that is waitable to get the result
    (or the exception) of the function.

    The arguments given here will be passed to thread's constructor, so use like:

    :param delay: seconds to wait before launching function

    >>> @call_in_separate_thread(daemon=True)
    >>> def handle_messages():
    >>>     while True:
    >>>         ...
    """

    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs) -> Future:
            class MyThread(threading.Thread):
                def __init__(self):
                    self.future = Future()
                    super().__init__(*t_args, **t_kwargs)

                def run(self):
                    if not self.future.set_running_or_notify_cancel():
                        return
                    if delay:
                        time.sleep(delay)
                    try:
                        res = fun(*args, **kwargs)
                        self.future.set_result(res)
                    except Exception as e:
                        self.future.set_exception(e)

            t = MyThread()
            t.start()
            return t.future

        return inner

    return outer


class Condition(PythonCondition):
    """
    A wrapper to faciliate easier usage of Pythons' threading.Condition.

    There's no need to acquire the underlying lock, as wait/notify/notify_all do it for you.

    This happens to sorta not work on PyPy. Use at your own peril. You have been warned.
    """

    def notifyAll(self) -> None:
        """
        Deprecated alias for notify_all

        .. deprecated:: 2.14.22
        """
        warnings.warn('Use notify_all instead', DeprecationWarning)
        self.notify_all()

    def wait(self, timeout: tp.Optional[tp.Union[str, float]] = None,
             dont_raise: bool = False) -> None:
        """
        Wait for condition to become true.

        :param timeout: timeout to wait. None is default and means infinity. Can be also a
            time string.
        :param dont_raise: if True, then WouldWaitMore won't be raised
        :raises ResourceLocked: unable to acquire the underlying lock within specified timeout.
        :raises WouldWaitMore: wait's timeout has expired
        """
        if timeout is not None:
            timeout = parse_time_string(timeout)
            if timeout < 0:
                timeout = 0

        with measure(timeout=timeout) as measurement:
            if timeout is None:
                self.acquire()
            else:
                if not self.acquire(timeout=measurement.time_remaining):
                    raise ResourceLocked('internal lock locked')

            try:
                if timeout is None:
                    super().wait()
                else:
                    if not super().wait(timeout=measurement.time_remaining):
                        if not dont_raise:
                            raise WouldWaitMore('wait was not notified')
            finally:
                self.release()

    def notify_all(self) -> None:
        """
        Notify all threads waiting on this Condition
        """
        with self._lock:
            super().notify_all()

    def notify(self, n: int = 1) -> None:
        """
        Notify n threads waiting on this Condition

        :param n: amount of threads to notify
        """
        with self._lock:
            super().notify(n=n)


class SingleStartThread(threading.Thread):
    """
    A thread that keeps track of whether it's .start() method was called, and does nothing
    if it's called second or so time.
    """

    def __init__(self, *args, **kwargs):
        self.__started = False
        super().__init__(*args, **kwargs)

    def start(self) -> 'SingleStartThread':
        """
        No-op when called second or so time. The first time it starts the thread.

        :return: self
        """
        if self.__started:
            return
        self.__started = True
        super().start()
        return self


class BogusTerminableThread:
    """
    A mock object that implements threading interface but does nothing

    :ivar running: bool, if it's running
    :ivar terminated: bool, if terminated
    :ivar daemon: bool, if daemon
    """
    __slots__ = ('running', 'terminated', 'daemon')

    def __init__(self):
        self.running = False
        self.terminated = False
        self.daemon = True

    def is_alive(self) -> bool:
        """
        :return: if this thread is alive
        """
        return not self.terminated and self.running

    def start(self) -> None:
        """
        Set running to True
        :raises RuntimeError: thread already terminated or already running
        """
        if self.terminated:
            raise RuntimeError('Thread already terminated')
        if self.running:
            raise RuntimeError('Thread already running')
        self.running = True

    def terminate(self) -> None:
        """
        Set terminated to True.

        Note that to set running to False you need to invoke
        :meth:`~satella.coding.concurrent.BogusTerminableThread.join` afterwards.
        """
        self.terminated = True

    def join(self, timeout=None) -> None:
        """
        Wait for the pseudo-thread. Sets running to False if thread was terminated.
        """
        if self.terminated:
            self.running = False


class TerminableThread(threading.Thread):
    """
    Class that will execute something in a loop unless terminated. Use like:

    >>> class MeGrimlock(TerminableThread):
    >>>     def loop(self):
    >>>         ... do your operations ..
    >>> a = MeGrimlock().start()
    >>> a.terminate().join()

    Property to check whether to terminate is stored in **self.terminating**.

    If you decide to override run(), you got to check periodically for **self._terminating**
    to become true. If it's true, then a termination request was received, and the thread should
    terminate itself.
    If you decide to use the loop/cleanup interface, you don't need to do so, because it will
    be automatically checked for you before each loop() call.

    You may also use it as a context manager. Entering the context will start the thread, and
    exiting it will .terminate().join() it, in the following way:

    >>> a = MeGrimlock()
    >>> with a:
    >>>     ...
    >>> self.assertFalse(a.is_alive())
    """

    def __init__(self, *args, terminate_on: tp.Optional[ExceptionList] = None,
                 **kwargs):
        """
        Note that this is called in the constructor's thread. Use .prepare() to
        run statements that should be ran in new thread.

        :param terminate_on: if provided, and
            :meth:`~satella.coding.concurrent.TerminableThread.loop` throws one of it,
            swallow it and terminate the thread by calling
            :meth:`~satella.coding.concurrent.TerminableThread.terminate`. Note that the
            subclass check will be done via `isinstance` so you can use the metaclass magic :)
            Note that SystemExit will be automatically added to list of terminable exceptions.
        """
        super().__init__(*args, **kwargs)
        self._terminating = False  # type: bool
        if terminate_on is None:
            terminate_on = (SystemExit, )
        elif isinstance(terminate_on, tuple):
            terminate_on = (SystemExit, *terminate_on)
        else:
            terminate_on = (SystemExit, terminate_on)
        self._terminate_on = terminate_on

    @property
    def terminating(self) -> bool:
        """Return whether a termination of this thread was requested"""
        return self._terminating

    def prepare(self) -> None:
        """
        This is called before the .loop() looping loop is entered.

        This is invoked already in a separate thread.
        """

    def loop(self) -> None:
        """
        Run one iteration of the loop. Meant to be overrided. You do not need to override it
        if you decide to override run() through.

        This should block for as long as a single check will take, as termination checks take place
        between calls.

        Note that if it throws one of the exceptions given in `terminate_on` this thread will
        terminate cleanly, whereas if it throws something else, the thread will be terminated with
        a traceback.
        """

    def start(self) -> 'TerminableThread':
        """
        Start the execution of this thread
        :return: this thread
        """
        super().start()
        return self

    def run(self) -> None:
        """
        Calls self.loop() indefinitely, until terminating condition is met
        """
        try:
            self.prepare()
            while not self._terminating:
                try:
                    self.loop()
                except Exception as e:
                    if self._terminate_on is not None:
                        if isinstance(e, self._terminate_on):
                            self.terminate()
                    else:
                        raise
        except SystemExit:
            pass
        finally:
            self.cleanup()

    def cleanup(self):
        """
        Called after thread non-forced termination, in the thread's context.

        The default implementation does nothing.
        """

    def __enter__(self):
        """Returns self"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate().join()
        return False

    def safe_wait_condition(self, condition: Condition, timeout: tp.Union[str, float],
                            wake_up_each: tp.Union[str, float] = 2) -> None:
        """
        Wait for a condition, checking periodically if the thread is being terminated.

        To be invoked only by the thread that's represented by the object!

        :param condition: condition to wait on
        :param timeout: maximum time to wait in seconds. Can be also a time string
        :param wake_up_each: amount of seconds to wake up each to check for termination.
            Can be also a time string.
        :raises WouldWaitMore: timeout has passed and Condition has not happened
        :raises SystemExit: thread is terminating
        """
        timeout = parse_time_string(timeout)
        wake_up_each = parse_time_string(wake_up_each)
        t = 0
        while t < timeout:
            if self._terminating:
                raise SystemExit()
            ttw = min(timeout-t, wake_up_each)
            t += ttw
            try:
                condition.wait(ttw)
                return
            except WouldWaitMore:
                pass
        raise WouldWaitMore()

    def safe_sleep(self, interval: float, wake_up_each: float = 2) -> None:
        """
        Sleep for interval, waking up each wake_up_each seconds to check if terminating,
        finish earlier if is terminating.

        This will do *the right thing* when passed a negative interval.

        To be invoked only by the thread that's represented by the object!

        :param interval: Time to sleep in total
        :param wake_up_each: Amount of seconds to wake up each
        :raises SystemExit: thread is terminating
        """
        t = 0
        while t < interval and not self._terminating:
            remaining_to_sleep = min(interval - t, wake_up_each)
            time.sleep(remaining_to_sleep)
            t += remaining_to_sleep
        if self._terminating:
            raise SystemExit()

    @property
    def terminating(self) -> bool:
        """
        :return: Is this thread either alive and trying to terminate or dead and after termination?
        """
        return self._terminating

    def terminate(self, force: bool = False) -> 'TerminableThread':
        """
        Signal this thread to terminate.

        Forcing, if requested, will be done by injecting a SystemExit exception into target
        thread, so the thread must acquire GIL. For example, following would not be interruptable:

        >>> time.sleep(1000000)

        Note that calling force=True on PyPy won't work, and NotImplementedError will be raised
        instead.

        :param force: Whether to force a quit
        :return: self
        :raises RuntimeError: when something goes wrong with the underlying Python machinery
        :raises NotImplementedError: force=True was used on PyPy
        """
        self._terminating = True
        if force:
            if platform.python_implementation() == 'PyPy':
                raise NotImplementedError('force=True was made on PyPy')
            ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self._ident),
                                                             ctypes.py_object(SystemExit))
            if ret == 0:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self._ident), 0)
                raise RuntimeError('Zero threads killed!')
            elif ret > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self._ident), 0)
                raise RuntimeError('Multiple threads killed!')

        return self


class IntervalTerminableThread(TerminableThread, metaclass=ABCMeta):
    """
    A TerminableThread that calls .loop() once per x seconds.

    If executing .loop() takes more than x seconds, on_overrun() will be called.

    :param seconds: time that a single looping through should take in seconds.
        Can be also a time string. This will include the time spent on calling .loop(), the rest
        of this time will be spent safe_sleep()ing.
    """

    def __init__(self, seconds: tp.Union[str, float], *args, **kwargs):
        self.seconds = parse_time_string(seconds)
        super().__init__(*args, **kwargs)

    @abstractmethod
    def loop(self) -> None:
        """
        Override me!
        """

    def on_overrun(self, time_taken: float) -> None:
        """
        Called when executing .loop() takes more than x seconds.

        Called each cycle.

        :param time_taken: how long did calling .loop() take
        """

    def run(self):
        self.prepare()
        while not self._terminating:
            with measure() as measurement:
                self.loop()
            time_taken = measurement()
            time_to_sleep = self.seconds - time_taken
            if time_to_sleep < 0:
                self.on_overrun(time_taken)
            else:
                self.safe_sleep(time_to_sleep)
        self.cleanup()
