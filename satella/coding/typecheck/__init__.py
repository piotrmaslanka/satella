# coding=UTF-8
from __future__ import print_function, absolute_import, division

"""
Decorator for debug-time typechecking

If you are simultaneously using @typed and @coerce, use them in following order:

    @coerce(...)
    @typed(...)
    def fun(..):
        ...

"""

from .basics import *
from .argparse import *
from .decorators import *

from .decorators import __all__ as __all_decorators__
from .argparse import __all__ as __all_argparse__
from .basics import __all__ as __all_basics__

__all__ = filter(lambda p: not p.startswith('_'),
                 __all_decorators__ + __all_argparse__ + __all_basics__)
