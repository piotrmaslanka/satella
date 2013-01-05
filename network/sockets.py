from satella.network.exceptions import DataUnavailableException, ConnectionFailedException
from socket import error as SocketError

class BaseSocket(object):
    """Basic wrapper class around a socket. NOT THREADSAFE"""
    def __init__(self, socket):
        """
        @param socket: socket object to wrap around
        """
        self.socket = socket    #: socket object wrapped
        self.tx = bytearray()   #: tx buffer
        self.rx = bytearray()   #: rx buffer

    # STUFF THAT CAN BE OVERLOADED/EXTENDED
    def has_expired(self):
        """
        Overload this.
        @return bool - whether the socket should be forcibly closed due to inactivity
        """
        return False
    def on_read(self):
        """
        Extend this, invoking inherited method at the beginning of your own.
        Internal signal from select that this socket can be read. THROWS L{socket.error}
        """
        try:
            self.rx.extend(self.socket.recv(1024))
        except SocketError:
            raise ConnectionFailedException, 'recv failed'

    def send(self, data):
        """
        Extend this, invoking inherited method at the end of your own with raw data to send.
        Queues data to be sent. You can override it so that it receives and sends your 
        objects, which could represent protocol frames, or such.
        """
        self.tx.extend(data)

    def peek(self, ln):
        """
        Extend this. Returns data from the buffer without removing it
        """
        if len(self.rx) < ln:
            raise DataUnavailableException, 'Not enough data in buffer'
        return self.rx[:ln]

    def read(self, ln):
        """
        Extend this. Returns data from the buffer, removing it after
        """
        if len(self.rx) < ln:
            raise DataUnavailableException, 'Not enough data in buffer'
        k = self.rx[:ln]
        del self.rx[:ln]
        return k

    def has_data(self, ln):
        """Extend/override this. Returns whether a read request of ln bytes can be satisfied right away"""
        return len(self.rx) >= ln

    def on_close(self):
        """Override this. Invoked when the socket is discarded by the select layer"""
        pass

    # Stuff that you should leave alone
    def wants_to_write(self):
        """
        Returns whether this socket wants to send data. Used by select to determine whether it should go
        into the select loop
        """
        return len(self.rx) > 0

    def fileno(self): return self.socket.fileno()

    def on_write(self):
        """Internal signal from slect that this socket can be written. THROWS L{socket.error}"""
        try:
            dw = self.socket.send(self.tx)
        except SocketError:
            raise ConnectionFailedException, 'send failed'
        del self.tx[:dw]

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