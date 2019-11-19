import logging
import typing

logger = logging.getLogger(__name__)


class BaseSatellaException(Exception):
    def __init__(self, msg):
        super(BaseSatellaException, self).__init__()
        self.msg = msg

    def __str__(self):
        return 'BaseSatellaException(%s)' % (repr(self.msg), )


class ResourceLocked(BaseSatellaException):
    """Given resource has been already locked"""


class ResourceNotLocked(BaseSatellaException):
    """Locking given resource is needed in order to access it"""
