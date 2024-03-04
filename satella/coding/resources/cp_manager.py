import abc
import logging
import queue
import sys
import typing as tp
import warnings

from ..concurrent import Monitor
from ..misc import Closeable
from ..recast_exceptions import silence_excs
from ..typing import T

logger = logging.getLogger(__name__)


class CPManager(Monitor, Closeable, tp.Generic[T], metaclass=abc.ABCMeta):
    """
    A thread-safe no-hassle connection-pool manager.

    Extend this class to build your own connection pool managers.

    This supports automatic connection recycling, connection will be cycled each
    max_cycle_no takings and deposits.

    Note that you have to overload :meth:`~satella.coding.resources.CPManager.teardown_connection`
    and :meth:`~satella.coding.resources.CPManager.create_connection`.

    You obtain a connection by using :meth:`~satella.coding.resources.CPManager.acquire_connection`.
    If it fails you should mark it as such using
    :meth:`~satella.coding.resources.CPManager.fail_connection`.
    In all cases you have to return it using
    :meth:`~satella.coding.resources.CPManager.release_connection`.

    :param max_number: maximum number of connections
    :param max_cycle_no: maximum number of get/put connection cycles.
    :ivar max_number: maximum amount of connections. Can be changed during runtime

    .. warning:: May not work under PyPy for reasons having to do with id's semantics.
        A RuntimeWarning will be issued when not running under CPython.
    """

    def __init__(self, max_number: int, max_cycle_no: int):
        Closeable.__init__(self)
        Monitor.__init__(self)
        if sys.implementation.name != 'cpython':
            warnings.warn(f'This may run bad on {sys.implementation.name}', RuntimeWarning)
        self.connections = queue.Queue(max_number)
        self.max_number = max_number
        self.max_cycle_no = max_cycle_no
        self.id_to_times = {}  # type: tp.Dict[int, int]
        self.terminating = False

    def close(self) -> None:
        if super().close():
            self.terminating = True
            self.invalidate()

    @Monitor.synchronized
    def invalidate(self) -> None:
        """
        Close all connections. Connections have to be released first. Object is ready for use after this
        """
        while self.connections.qsize() > 0:
            conn = self.connections.get()
            self.teardown_connection(conn)
            del self.id_to_times[id(conn)]

    def acquire_connection(self) -> T:
        """
        Either acquire a new connection, or just establish it in the background

        :return: a new connection:
        :raises RuntimeError: CPManager is terminating!
        """
        if self.terminating:
            raise RuntimeError('CPManager is terminating')
        try:
            conn = self.connections.get(False)
        except queue.Empty:
            while True:
                with silence_excs(queue.Empty), Monitor.acquire(self):
                    if self.connections.qsize() >= self.max_number:
                        conn = self.connections.get(False, 5)
                        break
                    else:
                        conn = self.create_connection()
                        break
        with Monitor.acquire(self):
            obj_id = id(conn)
            self.id_to_times[obj_id] = self.id_to_times.get(obj_id, 0) + 1
            return conn

    def release_connection(self, connection: T) -> None:
        """
        Release a connection

        :param connection: connection to release
        """
        obj_id = id(connection)
        if self.id_to_times[obj_id] >= self.max_cycle_no:
            self._kill_connection(connection)
        else:
            try:
                self.connections.put(connection, False)
            except queue.Full:
                self._kill_connection(connection)

    def _kill_connection(self, connection):
        obj_id = id(connection)
        with Monitor.acquire(self):
            del self.id_to_times[obj_id]

        self.teardown_connection(connection)

    @Monitor.synchronized
    def fail_connection(self, connection: T) -> None:
        """
        Signal that a given connection has been failed

        :param connection: connection to fail
        """
        self.id_to_times[id(connection)] = self.max_cycle_no

    @abc.abstractmethod
    def teardown_connection(self, connection: T) -> None:
        """
        Close the connection.

        Is safe to block.

        :param connection: connection to tear down
        """

    @abc.abstractmethod
    def create_connection(self) -> T:
        """
        Create a new connection.

        Is safe to block.

        :return: a new connection instance
        """
