from satella.channels.subtypes import FileDescriptorChannel
from satella.channels.exceptions import UnderlyingFailure, ChannelClosed, InvalidOperation, \
                                        TransientFailure, ChannelFailure
from satella.channels.base import HandlingLayer
import socket
import select

class Socket(FileDescriptorChannel):
    """
    A channel implementation of a network socket
    """

    def __init__(self, socket):
        FileDescriptorChannel.__init__(self)
        self.socket = socket
        self.active = True
        self.blocking = True
        self.timeout = None
        self.socket.settimeout(None)

    def write(self, data):
        if not self.active: raise ChannelClosed, 'cannot write - socket closed'

        if self.blocking:
            try:
                self.socket.send(data)
            except socket.timeout:
                raise TransientFailure, 'timeout on send'
            except socket.error:
                self.active = False
                raise UnderlyingFailure, 'send failed'
        else:
            self.tx_buffer.extend(data)
            self.on_writable()  # throws UnderlyingFailure, we'll let it propagate

    def read(self, count):
        if not self.active: raise ChannelClosed, 'cannot read - socket closed'

        if self.blocking:
            k = bytearray()
            while len(k) < count:
                try:
                    s = self.socket.recv(count-len(k))
                except socket.error:
                    self.active = False
                    raise UnderlyingFailure, 'socket recv failed'
                except socket.timeout:
                    raise DataNotAvailable, 'timeout on recv'

                if len(s) == 0:
                    self.active = False
                    raise ChannelClosed, 'gracefully closed'

                k.extend(s)

            return k
        else:
            return FileDescriptorChannel.read(self, count)

    def close(self):
        if not self.active: raise ChannelClosed, 'cannot close - socket closed'

        if self.blocking:
            self.socket.close()
        else:
            self.active = False
            # socket will be physically closed upon discard from handling layer,
            # and on_closed() will be called

    def settimeout(self, timeout):
        self.socket.settimeout(timeout)
        FileDescriptorChannel.settimeout(self, timeout)

    # -------------------------------------------- Handling non-blocking methods

    def on_writable(self):
        """Called by the handling layer upon detecting that this socket is writable
        and wants to send data. 

        Cannot be called if socket is blocking"""
        try:
            ki = self.socket.send(self.tx_buffer)
        except socket.error:
            self.active = False
            raise UnderlyingFailure, 'send() failed'

        del self.tx_buffer[ki:]

    def on_readable(self):
        """Called by the handling layer upon detecting that this socket is readable.
        Cannot be called if socket is blocking"""
        try:
            s = self.socket.recv(1024)
        except socket.error:
            self.active = False
            raise UnderlyingFailure, 'recv() failed'

        if len(s) == 0:
            self.active = False
            raise ChannelClosed, 'gracefully closed'

        self.rx_buffer.extend(s)

    def on_closed(self):
        """Called by the handling layer upon discarding the socket"""
        self.socket.close()

    def is_write_pending(self):
        """Returns whether this socket wants to send data. Useful only in non-blocking"""
        return len(self.rx_buffer) > 0

    def fileno(self):
        return self.socket.fileno()

class ServerSocket(FileDescriptorChannel):
    """
    A channel with server sockets
    """

    def __init__(self, socket):
        FileDescriptorChannel.__init__(self)
        self.socket = socket
        self.blocking = True
        self.active = True
        self.socket.settimeout(0)

    def write(self, data):
        raise InvalidOperation, 'server socket does not support that'

    def read(self, count):
        """@return: usually tuple (socket, remote peer address)"""
        if not self.active: raise ChannelClosed, 'cannot read - socket closed'

        try:
            return self.socket.accept()
        except socket.timeout:
            raise DataNotAvailable, 'no socket to accept'
        except socket.error:
            self.active = False
            raise UnderlyingFailure, 'accept() failed'

    def close(self):
        if not self.active: raise ChannelClosed, 'cannot close - socket closed'

        self.active = False

        if self.blocking:
            self.socket.close()
        else:
            pass
            # socket will be physically closed upon discard from handling layer
            
    def settimeout(self, timeout):
        self.socket.settimeout(timeout)
        FileDescriptorChannel.settimeout(self, timeout)

    # -------------------------------------------- Handling non-blocking methods

    def on_writable(self):
        pass

    def on_readable(self):
        pass

    def on_closed(self):
        self.socket.close()

    def is_write_pending(self):
        return False

    def fileno(self):
        return self.socket.fileno()

class SelectHandlingLayer(HandlingLayer):
    """A select-based handling layer"""
    def __init__(self):
        HandlingLayer.__init__(self)

    def register_channel(self, channel):
        """
        Registers a file descriptor based channel.

        Throws L{ValueError} is this is not a file descriptor based channel
        """
        if not isinstance(channel, FileDescriptorChannel):
            raise ValueError, 'Not a file descriptor based channel'

        channel.settimeout(0)

        if not hasattr(channel, 'is_write_pending'):
            raise ValueError, 'is_write_pending() method lacking'

        self.channels.append(channel)

    def unregister_channel(self, channel):
        try:
            self.channels.remove(channel)
        except ValueError:
            raise ValueError, 'channel not found'


    def __close_channel(self, channel):
        self.channels.remove(channel)
        channel.on_closed()
        self.on_closed(channel)

    def select(self, timeout=5):
        writables = [x for x in self.channels if x.is_write_pending()]
        try:
            rs, ws, xs = select.select(self.channels, writables, (), timeout)
        except select.error:
            # we need to trace over each channel to determine who has failed
            for channel in self.channels:
                try:
                    select.select((channel, ), (), (), 0)
                except select.error:
                    # we found the one
                    self.__close_channel(channel)
                    return

        except socket.error:
            raise RuntimeError, 'ABEND: socket error in select loop'

        # Now, for each writeable channel...
        for writable in ws:
            try:
                writable.on_writable()
            except ChannelFailure:
                self.__close_channel(channel)
                return
            self.on_writable(writable)

        # For each readable channel...
        for readable in rs:
            try:
                readable.on_readable()
            except ChannelFailure:
                self.__close_channel(channel)
                return
            self.on_readable(channel)

