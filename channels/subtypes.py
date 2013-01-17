from satella.channels.base import Channel

class FileDescriptorChannel(Channel):
    """
    This channel is based upon a file descriptor, and as such
    may require different type of handling layer
    """