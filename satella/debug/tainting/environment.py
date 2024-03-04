from __future__ import annotations

import dis
import gc
import sys
import threading
import typing as tp
import warnings

from satella.coding.typing import T
from .tainteds import TaintedObject, access_tainted, taint

local = threading.local()

RET_VAL = dis.opmap['RETURN_VALUE']


class TaintingEnvironment:
    """
    A round of tainting. Taints will be invalidated at the end.
    Basically any Python opcode that relates to tainting will
    be tainted itself.

    As an added extra, function values will be tainted as well if at least one of the parameters has been tainted

    Use like this:

    >>> with TaintingEnvironment() as env:
    >>>     a = taint(a)
    >>>     b = a + 5
    >>>     ...

    .. warning:: Using environment tainting will slow down your Python scripts since they install a per opcode handler.

    .. warning:: Using functions that take at least one tainted argument is supposed to return a tainted result,
        but I couldn't get that shipped in time at this involved some serious tweaking with the Python bytecode.
    """
    __slots__ = 'enabled', 'old_python'

    def __init__(self):
        vi = sys.version_info
        self.old_python = False
        if vi.major >= 3 and vi.minor < 7:
            warnings.warn(
                'Due to an old Python being used, altering function return values to be tainted will not work',
                UserWarning)
            self.old_python = True
        elif sys.implementation.name != 'cpython':
            warnings.warn(
                'You are not using CPython. Since this library will eventually involve some tweaking with the Python '
                'bytecode, if your runtime does not provide this level of compatibility, it will not work.',
                UserWarning)

        self.enabled = False

    def __enter__(self) -> TaintingEnvironment:
        """
        Register itself as the current tainting environment

        :raises RuntimeError: there is already a tainting session in progress
        """
        self.enabled = True
        global local
        if hasattr(local, 'satella_tainting'):
            raise RuntimeError('Other tainting session in progress')
        local.satella_tainting = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del local.satella_tainting
        self.enabled = False
        return False

    @staticmethod
    def get_session_in_progress() -> TaintingEnvironment:
        """
        Obtain current tainting session in progress

        :raises RuntimeError: no tainting session started yet
        """
        if not hasattr(local, 'satella_tainting'):
            raise RuntimeError('You require a session in progress to do that')
        return local.satella_tainting

    def get_tainted_variables(self) -> tp.Iterator[T]:
        """
        Return all, of the tainted variables
        """
        for obj in gc.get_referrers(self):
            if not isinstance(obj, TaintedObject):
                continue
            yield access_tainted(obj)
