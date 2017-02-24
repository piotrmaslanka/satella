# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import functools
from satella.coding import CallableGroup
import posix
"""
POSIX components of .state.

Contract (with satella/state/__init__) is that this will raise ImportError if not running posix
"""


logger = logging.getLogger(__name__)


class CurrentPOSIXProcess(object):
    def __init__(self):
        self.on_before_fork = CallableGroup()  # to call BEFORE forking
        self.on_after_fork = CallableGroup()    # to call AFTER forking, (is_child: bool)

_myself = CurrentPOSIXProcess()


import os

@functools.wraps(os.fork)
def _monkeyFork():
    # os.fork() is replaced with that
    _myself.on_before_fork()
    pid = os.fork()
    _myself.on_after_fork(pid == 0)  # on_after_fork(is_child::bool)
    return pid

os.fork = _monkeyFork
