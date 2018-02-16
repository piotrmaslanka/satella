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
from .core_typecheck import *
from .decorators import *

