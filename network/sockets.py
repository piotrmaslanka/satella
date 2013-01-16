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
        self._valid = True   #: invalid socket will be removed by handling layer

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
        Internal signal from select that this socket can be read. 
        THROWS L{ConnectionFailedException}
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
        Extend this. Returns data from the buffer without removing it.
        Throws L{DataUnavailableException} when there's no data to satisfy the request
        """
        if len(self.rx) < ln:
            raise DataUnavailableException, 'Not enough data in buffer'
        return self.rx[:ln]

    def read(self, ln):
        """
        Extend this. Returns data from the buffer, removing it after.
        Throws L{DataUnavailableException} when there's no data to satisfy the request
        """
        if len(self.rx) < ln:
            raise DataUnavailableException, 'Not enough data in buffer'
        k = self.rx[:ln]
        del self.rx[:ln]
        return k

    def has_data(self, ln):
        """Extend/override this. Returns whether a read request of ln bytes can be satisfied right away"""
        return len(self.rx) >= ln

    def is_valid(self):
        """Returns whether the socket is valid"""
        return self._valid

    def invalidate(self):
        """Mark the socket as invalid. 

        This is an userland routine, can be used by
        the user to mark that socket as expedient - handling layer may opt to trash
        the socket withour a prior call to invalidate."""
        self._valid = False

    # Stuff that you should leave alone
    def wants_to_write(self):
        """
        Returns whether this socket wants to send data. 

        Called by handling layer to determine whether it should be checked for write buffer size
        """
        return len(self.tx) > 0

    def fileno(self):
        """Returns socket's descriptor number for handling layer. 

        Don't define if doesn't make sense.
        Throws L{ConnectionFailedException} on underlying socket failure"""
        try:
            return self.socket.fileno()
        except SocketError:
            raise ConnectionFailedException, 'fileno failed'

    def on_write(self):
        """Calling this means this socket can be written. 

        Invoked by handling layer. 
        Throws L{ConnectionFailedException} on underlying socket failure"""
        try:
            dw = self.socket.send(self.tx)
        except SocketError:
            raise ConnectionFailedException, 'send failed'
        del self.tx[:dw]

    def close(self):
        """Closes underlying socket. 

        Invoked by handling layer. No further calls
        will be made to this socket nor will it be referenced by the socket layer"""
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