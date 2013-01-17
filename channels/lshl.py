"""
LockSignalledChannel handling layer
"""

from satella.channels.exceptions import InvalidOperation
from satella.channels.base import HandlingLayer
from satella.channels.subtypes import LockSignalledChannel

class LockSignalledChannelHandlingLayer(HandlingLayer):
    """
    A handling layer for non-blocking L{LockSignalledChannel}s