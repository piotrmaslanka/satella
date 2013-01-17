from satella.channels.exceptions import DataNotAvailable, ChannelClosed, UnderlyingFailure


class Channel(object):
    """
    Channel is a helpful abstraction of a stream

    Channel is a byte-oriented stream that can fail and is aware of it.
    It can be a socket, serial port, or some sort of server abstaction. Many
    channels can be simultaneously waited upon.

    It can be waiting to read data from it, or it can be full and needs to wait
    before writing can be continued.

    A channel can be used both in blocking and non-blocking mode.

    Sample implementations provided here. You can feel free to override them,
    lest they provide the same functionality.

    If socket defines the fileno() method, then it will be regarded as it's file descriptor,
    so that handling logics such as select or epoll can be used against it
    """
    def __init__(self):
        self.tx_buffer = bytearray()
        self.rx_buffer = bytearray()
        self.rxlen = 0      #: amount of data waiting in Rx buffer
        self.active = True
        self.timeout = None    #: blocking by default
        self.blocking = True

    def settimeout(self, timeout):
        """
        Sets channel's timeout.
        This may not always succeed, L{InvalidOperation} will
        be thrown if it can't

        @param timeout: Seconds of blocking, 0 for nonblocking, None for infinity blocking
        @type timeout: int or None
        """
        self.timeout = timeout
        self.blocking = (timeout > 0) or (timeout == None)

    def write(self, data):
        """
        Writes data down the channel. Will block if the channel
        needs to wait for data's transmission.

        Throws L{ChannelClosed} or L{UnderlyingFailure} on error

        @type data: bytearray or str
        """
        self.tx_buffer.extend(data)

    def read(self, count, less=False):
        """
        Reads given amount of data from the socket

        Will block if channel is blocking and data is not yet available

        Throws L{ChannelClosed} or L{UnderlyingFailure} on error
        Throws L{DataNotAvailable} if channel is non-blocking and there's no data yet

        @param count: Amount of bytes to read
        @type count: int

        @param less: Can return with less than count if such is the situation,
            zero-length strings included
        @type less: bool
        """
        if len(self.rx_buffer) < count:
            if less:
                k = self.rx_buffer
                self.rx_buffer = bytearray()
                self.rxlen = 0
                return k
            else:
                raise DataNotAvailable, 'Not enough data in buffer'
        k = self.rx_buffer[:count]
        del self.rx_buffer[:count]
        self.rxlen -= count
        return k


class HandlingLayer(object):
    """A collection of channels for easy multiplexing"""

    def __init__(self):
        self.channels = []

    def register_channel(self, channel):
        raise NotImplementedError, 'abstract method'

    def unregister_channel(self, channel):
        raise NotImplementedError, 'abstract method'

    def select(self, timeout=0):
        raise NotImplementedError, 'abstract method'


    # ---------- overload these methods for your own handling layer

    def on_iteration(self):
        """Called just before performing the select() call"""

    def on_readable(self, channel):
        """Invoked during select() if it has been determined that channel
        is readable
        @param channel: channel that is readable
        @type channel: L{Channel}
        """

    def on_writable(self, channel):
        """Invoked during select() if it has been determined that channel
        is writable
        @param channel: channel that is writable
        @type channel: L{Channel}
        """

    def on_closed(self, channel):
        """Handling layer is forcing the channel to be unregistered, as because
        it has become closed or failed. This is called on already closed channel.

        @param channel: channel that has failed
        @type channel: L{Channel}
        """
