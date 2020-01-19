import functools
import inspect
import logging
import threading

from ...exceptions import ResourceLocked, ResourceNotLocked

logger = logging.getLogger(__name__)


class LockedDataset:
    """
    A locked dataset. Subclass like

    >>> class MyDataset(LockedDataset):
    >>>     def __init__(self):
    >>>         super(MyDataset, self).__init__()
    >>>         self.mydata: str = "lol wut"
    >>>    @LockedDataset.locked
    >>>    def protected(self):
    >>>         self.mydata = "updated atomically"

    >>> mds = MyDataset()
    >>> with mds as md:
    >>>     md.mydata = "modified atomically"

    >>> try:
    >>>     with mds(blocking=True, timeout=0.5) as md:
    >>>         md.mydata = "modified atomically"
    >>> except ResourceLocked:
    >>>     print('Could not update the resource')

    If no lock is held, this class that derives from such will raise ResourceNotLocked upon
    element access while a lock is not being held
    """

    class InternalDataset(object):
        def __init__(self):
            self.lock = threading.Lock()
            self.locked = False
            self.args = ()

    def __init__(self):
        self.__internal = LockedDataset.InternalDataset()

    @staticmethod
    def locked(blocking=True, timeout=-1):
        def inner(f):
            @functools.wraps(f)
            def in_ner(self, *args, **kwargs):
                with self(blocking=blocking, timeout=timeout):
                    return f(self, *args, **kwargs)

            return in_ner

        return inner

    def __getattribute__(self, name):
        if inspect.ismethod(super(LockedDataset, self).__getattribute__(name)):
            return super(LockedDataset, self).__getattribute__(name)

        if not get_internal(self).locked:
            raise ResourceNotLocked('No lock held on this object for a read operation')

        return super(LockedDataset, self).__getattribute__(name)

    def __setattr__(self, key, value):
        if key == '_LockedDataset__internal':
            return super(LockedDataset, self).__setattr__(key, value)
        if not get_internal(self).locked:
            raise ResourceNotLocked('No lock held on this object for a write operation')
        return super(LockedDataset, self).__setattr__(key, value)

    def __call__(self, blocking=True, timeout=-1):
        get_internal(self).args = blocking, timeout
        return self

    def __enter__(self):
        args = get_internal(self).args

        if not get_internal(self).lock.acquire(*args):
            raise ResourceLocked('Could not acquire the lock on the object')
        get_internal(self).locked = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        get_internal(self).lock.release()
        get_internal(self).locked = False
        return False


def get_internal(self):
    return super(LockedDataset, self).__getattribute__('_LockedDataset__internal')
