from satella.channels.subtypes import FileDescriptorChannel
from satella.channels.exceptions import UnderlyingFailure, ChannelClosed, InvalidOperation, \
                                        TransientFailure, ChannelFailure
from satella.channels.base import HandlingLayer
import socket
import select

class Socket(FileDescriptorChannel):
    """
    A channel implementation of a network socket.

    If the socket is blocking, it is assumed that it is processed in a threading manner. Therefore
    fails during reads or writes will result in closing the socket.

    If the socket is nonblocking, it is assumed that it is handled via a handling layer. Therefore
    fails during reads or writes will result in marking the socket as not active (self.active=False)
    but it will be handling layer who will call on_closed(), which ultimately results in closing
    the socket.
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
                self.close()
                raise UnderlyingFailure, 'send failed'
        else:
            self.tx_buffer.extend(data)
            self.on_writable()  # throws UnderlyingFailure, we'll let it propagate

    def read(self, count, less=False, peek=False):
        if not self.active: 
            # If we cannot satisfy the request, we need to raise an exception
            # because we will never be able to do so
            if len(self.rx_buffer) == 0:  # this would always fail
                raise ChannelClosed, 'channel closed'

            if len(self.rx_buffer) >= count:
                # if we can safely satisfy the request right away, do it
                return FileDescriptorChannel.read(self, count, less, peek)
            else:
                # we cannot satisfy all of the request, only less might save us now
                # from raising an exception
                if less:
                    return FileDescriptorChannel.read(self, count, less, peek)   
                else:
                    raise ChannelClosed, 'channel closed`'            

        if self.blocking:
            while len(self.rx_buffer) < count:  # We might spend some time here
                try:
                    s = self.socket.recv(count-len(self.rx_buffer))
                except socket.error:
                    self.close()
                    raise UnderlyingFailure, 'socket recv failed'
                except socket.timeout:
                    raise DataNotAvailable, 'timeout on recv'

                self.rx_buffer.extend(s)

                if len(s) == 0:
                    self.close()
                    # The channel has been closed right now. Invoke a recursive
                    # call to this function, it will do the necessary checking, 
                    # because now it will be true that self.active == False
                    return Socket.read(self, count, less, peek)

                if less:    # a single recv passed, we can return with less data
                    return FileDescriptorChannel.read(self, count, less, peek)

        return FileDescriptorChannel.read(self, count, less, peek)

    def close(self):
        if self.blocking:
            if self.active != False:
                self.socket.close()
        else:
            pass
            # socket will be physically closed upon discard from handling layer,
            # and on_closed() will be called

        self.active = False

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
            self.close()
            raise UnderlyingFailure, 'send() failed'

        del self.tx_buffer[:ki]

    def on_readable(self):
        """Called by the handling layer upon detecting that this socket is readable.
        Cannot be called if socket is blocking"""
        try:
            s = self.socket.recv(1024)
        except socket.error:
            self.close()
            raise UnderlyingFailure, 'recv() failed'

        if len(s) == 0:
            self.close()
            raise ChannelClosed, 'gracefully closed'

        self.rx_buffer.extend(s)

    def on_closed(self):
        """Called by the handling layer upon discarding the socket"""
        self.socket.close()

    def is_write_pending(self):
        """Returns whether this socket wants to send data. Useful only in non-blocking"""
        return len(self.tx_buffer) > 0

    def fileno(self):
        return self.socket.fileno()

    def get_underlying_object(self):
        """Returns socket object this channel is based upon"""
        return self.socket

class ServerSocket(FileDescriptorChannel):
    """
    A channel with server sockets
    """

    def get_underlying_object(self):
        """Returns socket object this channel is based upon"""
        return self.socket

    def __init__(self, socket):
        FileDescriptorChannel.__init__(self)
        self.socket = socket
        self.blocking = True
        self.active = True
        self.socket.settimeout(None)

    def listen(self, backlog=10):
        """
        A facade to server socket's listen() call, because apps
        may prefer to first wrap the socket in this class, and
        invoke listen() when everything is already set up
        """
        try:
            self.socket.listen(backlog)
        except socket.error:
            raise ChannelFailure, 'listen failed'

    def write(self, data):
        raise InvalidOperation, 'server socket does not support that'

    def read(self):
        """@return: a new client L{Socket}"""
        if not self.active: raise ChannelClosed, 'cannot read - socket closed'

        try:
            return Socket(self.socket.accept()[0])
        except socket.timeout:            
            raise DataNotAvailable, 'no socket to accept'
        except socket.error:
            self.close()
            raise UnderlyingFailure, 'accept() failed'

    def close(self):
        """close itself can be called multiple times. calling this on a closed channel is
        a no-op"""
        # it could raise an exception, but we would usually process this in a try.. finally
        # therefore close() shouldn't really throw anything
        #if not self.active: raise ChannelClosed, 'cannot close - socket closed'
        if self.blocking:
            if self.active != False:
                self.socket.close()
        else:
            pass
            # socket will be physically closed upon discard from handling layer.

        self.active = False
            
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
        """
        Unregisters the channel from select layer.

        Channel remains in non-blocking mode, you must switch it back
        to blocking if you wish so.
        """
        try:
            self.channels.remove(channel)
        except ValueError:
            raise ValueError, 'channel not found'

    def close_channel(self, channel):
        """
        Channel unregister + channel close
        """
        channel.on_closed() # this should close the channel
        self.on_closed(channel)
        self.unregister_channel(channel)

    def select(self, timeout=5):
        self.on_iteration()

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
                self.close_channel(writable)
                return
            self.on_writable(writable)

        # For each readable channel...
        for readable in rs:
            try:
                readable.on_readable()
            except (ChannelFailure, ChannelClosed):
                self.close_channel(readable)
                return
            self.on_readable(readable)

