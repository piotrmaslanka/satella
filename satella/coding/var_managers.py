from __future__ import annotations

import typing as tp
import warnings
import threading

from satella.coding.structures import Proxy
from satella.exceptions import ImpossibleError, SatellaWarning, ReadonlyError

try:
    import gevent.monkey, gevent.socket
    import socket
    GEVENT_ENABLED = socket.socket is gevent.socket.socket
except ImportError:
    GEVENT_ENABLED = False


THREADED_ROOT: Context = None
THREADING_LOCK = threading.RLock()


class AssignWarning(Warning):
    """A warned assignment was done."""


def get_current_context() -> Context:
    pass

class SettingGlobalWarning(Warning):
    """A new global is being set warning."""


class Context(object):
    """
    A context to store your global data.

    You can use it as a standard attribute element, eg. threading.local()

    :param parent: parent to use
    :param data: data to use
    :param readonly: whether this context is read-only
    :param warn_on_assing: emit a AssignWarning on assigment
    :param assign_to_parent: assign value not found here to parent
    """
    __slots__ = 'parent', 'data', 'readonly', 'warn_on_assign', 'assign_to_parent'

    @classmethod
    def new_tree(cls, *args, **kwargs) -> Context:
        """
        Start a new tree starting with this context.

        Pass all parameters that you would pass to a constructor, save for parent. Don't pass that, it will be assumed
        to be None.
        """
        return cls(None, *args, **kwargs)

    def __bool__(self) -> bool:
        return bool(self.data)

    def lookup(self, key) -> tp.Iterable[Context]:
        """
        Return a iterable of contexts containing provided key.

        :param key: key to check for
        """
        if key in self.data:
            yield self
        if self.parent is not None:
            yield from self.parent.lookup(key)

    def __init__(self, parent: tp.Optional[Context] = None, data: tp.Optional[dict] = None, readonly: bool = False,
                 warn_on_assign: bool = False, assign_to_parent: bool = False):
        if parent is None:
            parent = get_current_context()
        super().__setattr__('parent', parent)
        super().__setattr__('data', data or {})
        super().__setattr__('readonly', readonly)
        super().__setattr__('warn_on_assign', warn_on_assign)
        super().__setattr__('assign_to_parent', assign_to_parent)

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        if self.parent is None:
            raise AttributeError(f'Attribute "{item}" not found')
        return getattr(self.parent, item)

    def __repr__(self) -> str:
        return f'%s(%s, %s, ...)' % (self.__class__.__name__, repr(self.parent), repr(self.data))

    def __setattr__(self, key, value):
        self.set(key, value)

    def set(self, key: str, value: object) -> None:
        """
        Set a global variable.

        :param key: key to set it as
        :param value: value to set it
        """
        print(self.data)
        if key in self.data:
            if self.readonly:
                raise ReadonlyError('This context is readonly')
            self.data[key] = value
        else:
            if self.warn_on_assign:
                warnings.warn(f'Warning on assign for {key}', AssignWarning)
            if self.assign_to_parent:
                self.parent.__setattr__(key, value)
            else:
                self.data[key] = value

        if self.parent is None:
            if self.readonly:
                raise ReadonlyError('This context is readonly')
            warnings.warn(f'New global {key} is being set', SettingGlobalWarning)
            self.data[key] = value

    def __delattr__(self, item):
        delattr(self.data, item)

    def new_context(self, use_threading: bool = None) -> Context:
        """
        Prepare a new context.

        :param use_threading: should this context be thread-ready
        """
        global THREADED_ROOT, THREADING_LOCK
        with THREADING_LOCK:
                THREADED_ROOT = (ThreadedContext if use_threading else Context)(THREADED_ROOT)
                return THREADED_ROOT

    def activate(self, _make_current_parent_this_parent: bool = True) -> Context:
        """
        Make this the current context

        :param _make_current_parent_this_parent: make currently registered context parent of this context
        :return: context currently in effect
        """
        global THREADED_ROOT, THREADING_LOCK

        with THREADING_LOCK:
            THREADED_ROOT = self
            if _make_current_parent_this_parent:
                self.parent = get_current_context()
        return self.parent

    def deactivate(self) -> Context:
        """Deactivate this context"""
        global THREADED_ROOT

        if self.parent is None:
            return self

        with THREADING_LOCK:
            if THREADED_ROOT is not self:
                raise ImpossibleError('Cannot deactivate a variable manager that is not the active one')
            assert THREADED_ROOT is self
            THREADED_ROOT = self.parent
        return self


class ThreadedContext(Context):
    """
    A thread-aware context
    """
    mydata = threading.local()

    def __init__(self, parent, data, *args, **kwargs):
        super().__init__(parent, data, *args, **kwargs)
        super().__setattr__('data', ThreadedContext.mydata)


THREADED_ROOT = Context()


class Current(Proxy):
    """A current context."""
    def __init__(self, context: Context):
        object.setattr(self, '_Proxy__obj', context)

    def _get_obj(self) -> object:
        return get_current_context()


def get_current_context(use_threading: tp.Optional[bool] = None) -> Context:
    """
    Return a context currently in use.

    :param use_threading: enable support for threading. Basically, contexts will be different between threads.
    :return: an instance of Context
    """
    if use_threading is None:
        use_threading = len(threading.enumerate()) > 1
        warnings.warn('Monkey-patching use_threading', SatellaWarning)

    global THREADED_ROOT
    with THREADING_LOCK:
        if THREADED_ROOT is None:
            THREADED_ROOT = Context(None, assign_to_parent=False)
        return THREADED_ROOT
        if THREADED_ROOT is None:
            THREADED_ROOT = ThreadedContext() if use_threading else Context()
            return THREADED_ROOT
        else:
            return THREADED_ROOT




