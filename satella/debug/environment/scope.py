from __future__ import annotations

import inspect
import threading
import typing as tp
import types
import weakref

from satella.coding import for_argument

EXCLUDED_VALUES = 'parent_scope', 'stack_frame'

SPECIAL_LOCK = threading.Lock()


class Scope:
    """
    A Scope. A Scope is always associated with a stack frame.

    Store attributes on it. If an attribute is not found, a lookup will be initiated
    upwards to the parent.

    Scope upon being destroyed will have it's options lifted upwards.

    :ivar parent_scope: (tp.Optional[Scope]) parent scope
    :ivar stack_frame: weak reference to the associated stack frame
    """
    def __init__(self, parent: tp.Optional[Scope] = None, stack_frame: tp.Optional[types.FrameType] = None):
        self.parent_scope = parent
        self.stack_frame = stack_frame or inspect.currentframe()

    def __getattr__(self, item):
        if self.parent_scope is None:       # root scope
            raise AttributeError(f'{item} not found')
        else:
            return getattr(self.parent_scope, item)

    @for_argument(returns=lambda y: '\n'.join(y))
    def __str__(self) -> str:
        yield '**** Scope values'
        for k, v in self.__dict__.items():
            if k not in EXCLUDED_VALUES:
                yield '****%s: %s' % (str(k), str(v))

    def __iter__(self) -> tp.Iterable[str]:
        return (k for k in self.__dict__ if k not in EXCLUDED_VALUES)

    def send_to_parent(self) -> None:
        """
        Send all currently stored data to immediate parent.

        Parent's dictionary will simply be overwritten.

        This will reset this scope's data
        """
        with SPECIAL_LOCK:
            from .tracing import local_data
            parent = local_data.current_scope
            my_dict = self._to_dict_for_raise()
            parent.__dict__.update(**my_dict)
            self.__dict__ = {'parent_scope': self.parent_scope,
                             'stack_frame': self.stack_frame}

    def _to_dict_for_raise(self) -> tp.Dict[str, tp.Any]:
        dict_for_raise = {}
        for k, v in self.__dict__.items():
            if k in EXCLUDED_VALUES:
                continue
            dict_for_raise[k] = v
        return dict_for_raise

    def reset_data(self) -> None:
        """
        Restore the data to pristine state. Will remove any data whatsoever from this Scope
        """
        self.__dict__ = {k: v for k, v in self.__dict__.items() if k not in EXCLUDED_VALUES}

    @staticmethod
    def get_current_scope() -> tp.Optional[Scope]:
        """
        Return current scope or None if not enabled.
        """
        from .tracing import ENVIRONMENT_ENABLED, local_data
        if ENVIRONMENT_ENABLED:
            if not hasattr(local_data, 'current_scope'):
                local_data.current_scope = Scope()
            return local_data.current_scope
