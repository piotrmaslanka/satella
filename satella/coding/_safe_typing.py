"""
This module exports a safe generic type and a type variable T to get around the bug in Python 3.5
https://github.com/python/typing/issues/498
"""
import typing as tp
import sys

__all__ = ['T', 'SafeGeneric']

T = tp.TypeVar('T')

if sys.version_info[1] == 5:
    SafeGeneric = object
else:
    SafeGeneric = tp.Generic[T]
