import abc
import sys
import typing as tp
import queue
import logging
import warnings

from ..concurrent import Monitor
from ..misc import Closeable
from ..recast_exceptions import silence_excs
from ..typing import T


logger = logging.getLogger(__name__)


class CPManager(Monitor, Closeable, tp.Generic[T]):
    """
    A thread-safe no-hassle connection-pool manager.

    This supports automatic connection recycling, connection will be cycled each
    max_cycle_no takings and deposits.

    Note that you have to overload :meth:`~satella.coding.resources.CPManager.teardown_connection`
    and :meth:`~satella.coding.resources.CPManager.create_connection`.

    :param max_number: maximum number of connections
    :param max_cycle_no: maximum number of get/put connection cycles.

    .. warning:: May not work under PyPy for reasons having to do with id's semantics.
    """

    def __init__(self, max_number: int, max_cycle_no: int):
        super().__init__()
        Closeable.__init__(self)
        if sys.implementation.name != 'cpython':
            warnings.warn(f'This may run bad on {sys.implementation.name}', UserWarning)
        self.connections = queue.Queue(max_number)
        self.spawned_connections = 0
        self.max_number = max_number
        self.max_cycle_no = max_cycle_no
        self.id_to_times = {}       # type: tp.Dict[int, int]

    def close(self) -> bool:
        if super().close():
            while self.spawned_connections:
                self.teardown_connection(self.connections.get())
                self.spawned_connections -= 1

    def acquire_connection(self) -> T:
        """
        Either acquire a new connection, or just establish it in the background
        """
        try:
            conn = self.connections.get(False)
        except queue.Empty:
            while True:
                with silence_excs(queue.Empty), Monitor.acquire(self):
                    if self.spawned_connections == self.max_number:
                        conn = self.connections.get(False, 5)
                        break
                    elif self.spawned_connections < self.max_number:
                        conn = self.create_connection()
                        self.connections.put(conn)
                        self.spawned_connections += 1
                        break
        obj_id = id(conn)
        try:
            self.id_to_times[obj_id] += 1
        except KeyError:
            self.id_to_times[obj_id] = 1
        return conn

    def release_connection(self, connection: T) -> None:
        """
        Release a connection

        :param connection: connection to release
        """
        obj_id = id(connection)
        if self.id_to_times[obj_id] == self.max_cycle_no:
            with Monitor.acquire(self), silence_excs(KeyError):
                self.spawned_connections -= 1
                del self.id_to_times[connection]

            self.teardown_connection(connection)
        else:
            try:
                self.connections.put(connection, False)
            except queue.Full:
                with Monitor.acquire(self), silence_excs(KeyError):
                    self.spawned_connections -= 1
                    del self.id_to_times[obj_id]
                self.teardown_connection(connection)

    def fail_connection(self, connection: T) -> None:
        """
        Signal that a given connection has been failed

        :param connection: connection to fail
        """
        obj_id = id(connection)
        self.id_to_times[obj_id] = self.max_cycle_no

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