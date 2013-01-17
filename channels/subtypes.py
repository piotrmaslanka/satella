from satella.channels.base import Channel
from satella.channels.exceptions import InvalidOperation, ChannelFailure, \
                                        TransientFailure, ChannelClosed, \
                                        DataNotAvailable
import Queue
from threading import Lock

class FileDescriptorChannel(Channel):
    """
    This channel is based upon a file descriptor, and as such
    may require different type of handling layer
    """

class LockSignalledChannel(Channel):
    """
    This channel's states are signalled by queueing it a message.
    This class is a monitor - it's threadsafe
    """

    class LSMReadable(object):
        """Data has arrived to this channel"""
        def __init__(self, lsc, data):
            self.lsc = lsc
            self.data = data

    class LSMFailed(object):
        """This channel has failed"""
        def __init__(self, lsc):
            self.lsc = lsc

    class LSMNothing(object):
        """Nothing has happened.
        REFACTOR THIS"""

    def __init__(self):
        Channel.__init__(self)
        self.handlinglayer = None

        self.blocking = False
        self.timeout = 0
        self.events = Queue.Queue()

        self.lock = Lock()


    def read(self, count, less=False):
        """
        Attempts to recover count bytes from the channel.

        If the channel is blocking and timeout is infinite, this will block for as long
        as necessary, unless it L{ChannelFailure}s first

        If the channel is blocking and timeout is finite, this will block for at most
        timeout returning data or L{DataNotAvailable} or L{ChannelFailure}

        If the channel is nonblocking, it will return L{DataNotAvailable} or the data
        """
        if not self.active: raise ChannelClosed

        with self.lock:
            if self.blocking:
                # uh, oh
                try:
                    return Channel.read(self, count)
                except DataNotAvailable:
                    if self.timeout != None:    # we need to hang for timeout at max
                        try:
                            msg = self.events.get(True, self.timeout)
                        except Queue.Empty:
                            if less:
                                return Channel.read(self, count, less)
                            else:
                                raise DataNotAvailable, 'no activity on channel for timeout'

                        if isinstance(msg, self.LSMReadable):
                            self.rx_buffer.extend(msg.data)
                            return Channel.read(self, count, less)  # throws DataNotAvailable, we'll let it propagate
                        elif isinstance(msg, self.LSMFailed):
                            self.active = False
                            raise ChannelFailure, 'channel failed'
                        elif isinstance(msg, self.LSMNothing):
                            return DataNotAvailable, 'data not yet available'
                    else:       # we may hang for eternity
                        while True:
                            try:
                                msg = self.events.get(True)
                            except Queue.Empty:
                                continue    # we may hang as long as we like

                            if isinstance(msg, self.LSMReadable):
                                self.rx_buffer.extend(msg.data)
                                try:
                                    return Channel.read(self, count, less)
                                except DataNotAvailable:
                                    continue    # no data? no problem, wait for more
                            elif isinstance(msg, self.LSMFailed):
                                self.active = False
                                raise ChannelFailure, 'channel failed'
                            elif isinstance(msg, self.LSMNothing):
                                pass    # do nothing
            else:
                while True:
                    try:
                        msg = self.events.get(False)
                    except Queue.Empty:
                        break

                    if isinstance(msg, self.LSMReadable):
                        self.rx_buffer.extend(msg.data)
                    elif isinstance(msg, self.LSMFailed):
                        self.active = False
                        raise ChannelFailure, 'channel failed'
                    elif isinstance(msg, self.LSMNothing):
                        pass    # do nothing

                return Channel.read(self, count, less)    # throws DataNotAvailable, let it propagate


    def is_write_pending(self):
        with self.lock:
            return len(self.tx_buffer) > 0

    def write(self, data):
        with self.lock:
            self.tx_buffer.extend(data)

    def settimeout(self, timeout):
        if self.blocking:
            self.timeout = timeout
        else:
            raise InvalidOperation, 'its nonblocking and you cant directly change that'

    # ----------------------------------------- called by handling layer
    def _on_foreign_data(self, data):
        """data has arrived from a thread that is not the handling layer.
        data and should be put on this channel"""
        if self.handlinglayer == None:
            # this is an unregistered channel
            self.events.put(self.LSMReadable(self, data))
        else:
            # registered channel, handling layer must be informed 
            self.handlinglayer.events.put(self.LSMReadable(self, data))

    def _on_foreign_fail(self):
        if self.handlinglayer == None:
            # this is an unregistered channel
            self.events.put(self.LSMFailed(self))
        else:
            # registered channel, handling layer must be informed 
            self.handlinglayer.events.put(self.LSMFailed(self))

    def _on_data(self, data):
        """data has arrived - this is called by handling layer, the same thread that 
        works this channel"""
        with self.lock:
            self.rx_buffer.extend(data)

    def _on_register(self, handlinglayer):
        """Channel is registered in a handling layer"""
        with self.lock:
            self.blocking = False
            self.timeout = 0
            self.handlinglayer = handlinglayer

    def _on_unregister(self):
        """Channel is unregistered from a handling layer"""
        with self.lock:
            self.blocking = True
            self.timeout = None
            self.handlinglayer = None