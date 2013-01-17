"""
Lock-signalled channels module
"""

from threading import Lock
from Queue import Queue

from satella.channels.subtypes import LockSignalledChannel


class ByteStreamChannel(LockSignalledChannel):
    def __init_