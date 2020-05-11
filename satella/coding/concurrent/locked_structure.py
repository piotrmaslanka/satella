import threading
import typing as tp

from ..structures.proxy import Proxy
T = tp.TypeVar('T')


class LockedStructure(Proxy, tp.Generic[T]):
    """
    A wizard to make every Python structure thread-safe.

    It wraps obj_to_wrap, passing on all calls, settings and so on to the object wrapper,
    from lock exposing only the context manager protocol.

    Example:

    >>> locked_dict = LockedStructure(dict)
    >>> with locked_dict:
    >>>     locked_dict[5] = 2
    
    Also, please note that operations such as addition will strip this object of being a locked
    structure, ie. they will return object that participated in locked structure plus some other.
    
    Note that in-place operations return the locked structure.
    """
    __slots__ = ('__lock',)

    def __init__(self, obj_to_wrap: T, lock: tp.Optional[threading.Lock] = None):
        super().__init__(obj_to_wrap)
        self.__lock = lock or threading.Lock()

    def __setattr__(self, key, value):
        if key == '_LockedStructure__lock':
            object.__setattr__(self, key, value)
        else:
            super().__setattr__(key, value)

    def __enter__(self):
        self.__lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__lock.release()
        return False
