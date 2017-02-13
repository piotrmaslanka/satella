# coding=UTF-8
"""
Things that run only during debug

If __debug__ is False, they will short-path themselves
"""
from __future__ import print_function, absolute_import, division

from satella.coding.debug.typecheck import typed