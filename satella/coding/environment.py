from __future__ import annotations

import threading
import typing as tp
import warnings

from satella.coding.typing import V

local = threading.local()

THEY_HATIN = object()


class Context:
    """
    New layer of environment. Can have it's own variables, or can hoist them onto the parent.

    .. warning:: This is considered experimental. I just haven't found out a good use case for it yet.
    """

    def __init__(self, parent: tp.Optional[Context] = None, **variables):
        warnings.warn('This is experimental', RuntimeWarning)
        self.parent = parent
        self.variables = variables
        self.bool = None

    def __str__(self):
        return str(id(self))

    def push_up(self, item: str, value=THEY_HATIN) -> None:
        """
        Advance current variable to the top of the card stack.

        :param item: variable name
        :param value: if not given, current value of given variable will be taken
        """
        if value is THEY_HATIN:
            var = self.variables.pop(item)
        else:
            var = value
        self.parent.variables[item] = var

    def __getattr__(self, item: str):
        if item in self.variables:
            v = self.variables[item]
            if v is not THEY_HATIN:
                return v
            raise AttributeError()
        if self.parent is not None:
            return getattr(self.parent, item)
        raise AttributeError()

    def __enter__(self):
        global local
        try:
            parent = local.thread_context
        except AttributeError:
            parent = None
        ctxt = Context(parent=parent)
        ctxt.parent = parent
        local.thread_context = ctxt
        return ctxt

    def __setattr__(self, key: str, value: V):
        """
        Set a value
        """
        if key in ('parent', 'variables', 'bool'):
            return super().__setattr__(key, value)
        else:
            self.variables[key] = value

    def __delattr__(self, item: str) -> None:
        self.variables[item] = THEY_HATIN

    def does_exist(self, val: str) -> bool:
        """
        Does a given value exist on stack for this call of function?
        """
        if val in self.variables:
            if self.variables[val] is THEY_HATIN:
                return False
            return True
        else:
            if self.parent is None:
                return False
            return self.parent.does_exist(val)

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self.parent is None:
            try:
                del local.thread_context
            except AttributeError:
                pass
        else:
            local.thread_context = self.parent
        return False

    @staticmethod
    def get() -> Context:
        """
        Return a local context for this thread
        """
        global local
        try:
            return local.thread_context
        except AttributeError:
            ctxt = Context()
            local.thread_context = ctxt
            return ctxt
