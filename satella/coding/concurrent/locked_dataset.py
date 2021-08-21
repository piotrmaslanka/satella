import inspect
import threading
import typing as tp

from ..decorators import wraps
from ...exceptions import ResourceLocked, ResourceNotLocked, WouldWaitMore


class LockedDataset:
    """
    A locked dataset. Subclass like

    >>> class MyDataset(LockedDataset):
    >>>     def __init__(self):
    >>>         super(MyDataset, self).__init__()
    >>>         with self:
    >>>             self.mydata: str = "lol wut"
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
    element access while a lock is not being held.

    Note that __enter__ will raise WouldWaitMore if timeout was given.
    """

    class InternalDataset:
        __slots__ = ('lock', 'locked', 'args')

        def __init__(self):
            self.lock = threading.Lock()
            self.locked = False
            self.args = ()

    def __init__(self):
        self.__internal = LockedDataset.InternalDataset()  # type: LockedDataset.InternalDataset

    @staticmethod
    def locked(blocking=True, timeout=-1) -> tp.Callable[[tp.Callable], tp.Callable]:
        """
        Decorator to use for annotating methods that would lock
        :param blocking: whether to block at all
        :param timeout: optional timeout. Default, or -1 means "return ASAP"
        """

        def inner(f):
            @wraps(f)
            def in_ner(self, *args, **kwargs):
                with self(blocking=blocking, timeout=timeout):
                    return f(self, *args, **kwargs)

            return in_ner

        return inner

    def __getattribute__(self, name):
        if inspect.ismethod(super(LockedDataset, self).__getattribute__(name)):
            return super(LockedDataset, self).__getattribute__(name)

        if not _get_internal(self).locked:
            raise ResourceNotLocked('No lock held on this object for a read operation')

        return super(LockedDataset, self).__getattribute__(name)

    def __setattr__(self, key, value):
        if key == '_LockedDataset__internal':
            return super(LockedDataset, self).__setattr__(key, value)
        if not _get_internal(self).locked:
            raise ResourceNotLocked('No lock held on this object for a write operation')
        return super(LockedDataset, self).__setattr__(key, value)

    def __call__(self, blocking: bool = True, timeout: float = -1):
        _get_internal(self).args = blocking, timeout
        return self

    def __enter__(self):
        args = _get_internal(self).args

        if not _get_internal(self).lock.acquire(*args):
            raise WouldWaitMore('Resource is still locked')
        _get_internal(self).locked = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _get_internal(self).lock.release()
        _get_internal(self).locked = False
        return False


def _get_internal(self):
    return super(LockedDataset, self).__getattribute__('_LockedDataset__internal')
