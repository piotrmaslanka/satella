# coding=UTF-8
"""
Global state, singletons and such a starting point.

This is imported during ANY module load
"""
from __future__ import print_function, absolute_import, division
import six
import os
import functools
import logging
from satella.coding import CallableGroup


logger = logging.getLogger(__name__)


try:
    from . import posixpart  # raises ImportError on non-POSIX systems

    _myself = posixpart._myself
except ImportError:
    # we are running on a non-POSIX system

    class CurrentNonPosixProcess(object):
        pass

    _myself = CurrentNonPosixProcess()


def getMe():
    """
    Return a Process object, representing current process.

    :return: a
    """
    return _myself
