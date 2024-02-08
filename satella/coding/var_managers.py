from __future__ import annotations
import typing as tp
import warnings

from satella.coding.structures import Singleton


GLOBAL_CONTEXT = Context()

class Readonly(Exception):
    """Context is read-only"""

class SettingGlobalWarning(Warning):
    """A new global is being set warning"""


class BaseContext(object):
    __slots__ = 'parent', 'data', 'readonly'

    def __init__(self, parent: tp.Optional[BaseContext] = None, readonly: bool = False):
        self.parent = parent
        self.data = {}
        self.readonly = readonly

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        if self.parent is None:
            raise AttributeError('Attribute not found')
        return getattr(self.parent, item)

    def __setattr__(self, key, value):
        if key in self.data:
            if self.readonly:
                raise Readonly('This context is readonly')
            self.data[key] = value

        if self.parent is None:
            if self.readonly:
                raise Readonly('This context is readonly')
            warnings.warn(f'New global {key} is being set', SettingGlobalWarning)
            self.data[key] = value

        setattr(self.data, key, value)

    def set(self, key: str, value: object, set_parent: bool = True) -> None:
        """
        Set a global variable

        :param key: key to set it as
        :param value: value to set it
        :param set_parent: if True and is possible to assign to parent, an assign will be attempted
        """
        if self.readonly:
            raise Readonly('This is read-only!')

        if not set_parent or key in self.data:
            self.data[key] = value
        else:


    def __delattr__(self, item):
        delattr(self.data, item)`


class EmptyContextManager:
    """
    A context manager that does nothing. Only to support conditional change of context managers,
    eg in such a way:

    >>> if tx_enabled:
    >>>     ctxt = transaction.atomic
    >>> else:
    >>>     ctxt = EmptyContextManager()
    >>> with ctxt:
    >>>     ...
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
