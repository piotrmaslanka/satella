from satella.channels.subtypes import FileDescriptorChannel
from satella.channels.exceptions import UnderlyingFailure, ChannelClosed, InvalidOperation, \
                                        TransientFailure, ChannelFailure
from satella.channels.base import HandlingLayer
import socket
import select

class Socket(FileDescriptorChannel):
    """
    A channel implementation of a TCP (or, in general, stream-oriented) network socket.

    If the socket is blocking, it is assumed that it is processed in a threading manner. Therefore
    fails during reads or writes will result in closing the socket.

    If the socket is nonblocking, it is assumed that it is handled via a handling layer. Therefore
    fails during reads or writes will result in marking the socket as not active (self.active=False)
    but it will be handling layer who will call on_closed(), which ultimately results in closing
    the socket.
    
    IMPORTANT!!! Take care to invoke parent methods if you are extending this class.
    """

    def __init__(self, _socket):
        """@type socket: native network socket or L{Socket}
        Whether socket is connected will be detected automatically by means
        of a zero-length write"""
        FileDescriptorChannel.__init__(self)
        if isinstance(_socket, Socket):
            self.socket = _socket.socket
        else:
            self.socket = _socket
        self.active = True
        self.blocking = True
        self.timeout = None
        self.socket.settimeout(None)

        # Detect whether socket is connected
        try:
            self.socket.send('')
        except socket.error as e:
            if e.errno in (10057, 11, 32):  
                # Resource temporarily unavailable or Broken pipe
                self.connected = False
            else:
                self.connected = True
        else:
            self.connected = True

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

    def connect(self, *args):
        """A pass-thru for socket's .connect()"""
        try:
            self.socket.connect(*args)
        except socket.error as e:
            # "Operation now in progress" exception
            if e.errno not in (115, 10035): raise
        if self.blocking:
            self.connected = True

    # -------------------------------------------- Handling non-blocking methods

    def on_connected(self):
        """Socket's .connect() has completed - successfully or not.
        self.connected has been already set accordingly

        Cannot be called if socket is blocking"""

    def on_writable(self):
        """Called by the handling layer upon detecting that this socket is writable
        and wants to send data. 

        Cannot be called if socket is blocking"""

        # If socket was EINPROGRESS and it has become readable, then it's connected
        # successfully or not. Mark it.
        if not self.connected:
            self.connected = True
            self.on_connected()
            if len(self.tx_buffer) == 0:
                return

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
        """Returns whether this socket wants to send data. Useful only in non-blocking.
        It will also return true if socket is EINPROGRESS, as it needs that to detect
        connection"""
        return (len(self.tx_buffer) > 0) or not self.connected

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
    
try:
    _BASELEVEL = select.POLLIN | select.POLLOUT | select.POLLERR | select.POLLHUP | select.POLLNVAL
    IS_POLL_SUPPORTED = True
except AttributeError:
    IS_POLL_SUPPORTED = False
    
class SelectHandlingLayer(HandlingLayer):
    """A select-based handling layer"""
    def __init__(self):
        HandlingLayer.__init__(self)
        
        if IS_POLL_SUPPORTED:
            self.poll = select.poll()
            self.fdmap = {}

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
        
        if IS_POLL_SUPPORTED:
            self.poll.register(channel, select.POLLIN | select.POLLERR | select.POLLHUP | select.POLLNVAL)
            self.fdmap[channel.fileno()] = channel

    def unregister_channel(self, channel):
        """
        Unregisters the channel from select layer.

        Channel remains in non-blocking mode, you must switch it back
        to blocking if you wish so.
        """
        try:
            self.channels.remove(channel)
            if IS_POLL_SUPPORTED:
                self.poll.unregister(channel)
                del self.fdmap[channel.fileno()]
        except (ValueError, KeyError, select.error):
            raise ValueError, 'channel not found'

    def close_channel(self, channel):
        """
        Channel unregister + channel close
        """
        self.unregister_channel(channel)
        if IS_POLL_SUPPORTED:
            try:
                self.poll.unregister(channel)
                del self.fdmap[channel.fileno()]
            except KeyError:
                pass
        channel.on_closed() # this should close the channel
        self.on_closed(channel)

    def select(self, timeout=5):
        self.on_iteration()

        if IS_POLL_SUPPORTED:           # Perform poll() event loop

            for x in self.channels:
                if x.is_write_pending():
                    self.poll.modify(x, _BASELEVEL | select.POLLOUT)  
                else:
                    self.poll.modify(x, _BASELEVEL)

            events = self.poll.poll(timeout)

            # Now, for each event...

            for fdinfo, event in events:
                channel = self.fdmap[fdinfo]

                if event & (select.EPOLLHUP | select.POLLERR | select.POLLNVAL):
                    self.close_channel(channel)
                    return

                if event & select.POLLIN:
                    try:
                        channel.on_readable()
                    except (ChannelFailure, ChannelClosed):
                        self.close_channel(channel)
                        return
                    self.on_readable(channel)

                if event & select.POLLOUT:
                    try:
                        if not channel.connected:
                            channel.on_writable()
                            self.on_connected(channel)
                        else:
                            channel.on_writable()
                    except ChannelFailure:
                        self.close_channel(channel)
                        return
                    self.on_writable(channel)
                    
        else:                           # Fall back to select()
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
                        self.close_channel(channel)
                        return
            except socket.error:
                raise RuntimeError, 'ABEND: socket error in select loop'

            # Now, for each writeable channel...
            for writable in ws:
                try:
                    if not writable.connected:
                        writable.on_writable()
                        self.on_connected(writable)
                    else:
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

