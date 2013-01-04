from satella.network.exceptions import DataUnavailableException, ConnectionFailedException
from socket import error as SocketError

class BaseSocket(object):
    """Basic wrapper class around a socket"""
    def __init__(self, socket):
        """
        @param socket: socket object to wrap around
        """
        self.socket = socket    #: socket object wrapped
        self.tx = bytearray()   #: tx buffer
        self.rx = bytearray()   #: rx buffer

    # Interface against select loop
    def has_expired(self):
        """Returns whether the socket should be forcibly closed due to inactivity"""
        return False
    def on_read(self):
        """Internal signal from select that this socket can be read. THROWS L{socket.error}"""
        try:
            self.rx.extend(self.socket.recv(1024))
        except SocketError:
            raise ConnectionFailedException, 'recv failed'
    def on_write(self):
        """Internal signal from slect that this socket can be written. THROWS L{socket.error}"""
        try:
            dw = self.socket.send(self.tx)
        except SocketError:
            raise ConnectionFailedException, 'send failed'
        del self.tx[:dw]
    def wants_to_write(self):
        """Returns whether this socket wants to send data"""
        return len(self.rx) > 0

    def fileno(self): return self.socket.fileno()

    def peek(self, ln):
        if len(self.rx) < ln:
            raise DataUnavailableException, 'Not enough data in buffer'
        return self.rx[:ln]

    def read(self, ln):
        if len(self.rx) < ln:
            raise DataUnavailableException, 'Not enough data in buffer'
        k = self.rx[:ln]
        del self.rx[:ln]
        return k

    def has_data(self, ln):
        """Returns whether a read request of ln bytes can be satisfied right away"""
        return len(self.rx) >= ln

    def send(self, data):
        """Queues data to be sent"""
        self.tx.extend(data)

    def close(self):
        """Closes the socket. NOEXCEPT"""
        try:
            self.socket.close()
        except:
            pass

class BasicTimeoutTrackingSocket(BaseSocket):
    """Basic extension of BaseSocket that tracks timeouts and deletes them if no data was received during
       a time period"""
    def __init__(self, socket, expiration, *args, **kwargs):
        """If no data is received on the socket for expiration seconds, it will be closed due to inactivity"""
        BaseSocket.__init__(self, socket, *args, **kwargs)
        self._last_received = time()
        self._expiration = expiration

    def on_read(self):
        BaseSocket.on_read(self)
        self._last_received = time()

    def has_expired(self):
        return (time() - self._last_received) > self._expiration