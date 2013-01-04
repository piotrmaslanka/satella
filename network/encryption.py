from ssl import SSLError

from satella.network.exceptions import ConnectionFailedException
from satella.network.sockets import BaseSocket

class SSLBaseSocket(BaseSocket):
    """Basic wrapper around a SSL-wrapped socket"""
    def on_read(self):
        try:
            BaseSocket.on_read(self)
        except SSLError:
            raise ConnectionFailedException, 'SSLError raised'

    def on_write(self):
        try:
            BaseSocket.on_write(self)
        except SSLError:
            raise ConnectionFailedException, 'SSLError raised'


class BasicSSLTimeoutTrackingSocket(SSLBaseSocket):
    """Basic extension of BaseSocket that tracks timeouts and deletes them if no data was received during
       a time period"""
    def __init__(self, socket, expiration, *args, **kwargs):
        """If no data is received on the socket for expiration seconds, it will be closed due to inactivity"""
        SSLBaseSocket.__init__(self, socket, *args, **kwargs)
        self._last_received = time()
        self._expiration = expiration

    def on_read(self):
        SSLBaseSocket.on_read(self)
        self._last_received = time()

    def has_expired(self):
        return (time() - self._last_received) > self._expiration