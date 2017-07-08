# coding=UTF-8
"""
UNIX things
"""
from __future__ import print_function, absolute_import, division
import six
import logging
import functools
import os
import warnings
from .daemon import daemonize
from .pidlock import AcquirePIDLock
from .signals import hang_until_sig


logger = logging.getLogger(__name__)


def is_running_as_root():
    """
    Is this process running as root?

    Checks whether EUID is 0
    :return: bool
    """
    return os.geteuid() == 0



try:
    os.fork
except AttributeError:
    logger.warn('Running on Windows, skipping fork')
else:
    @functools.wraps(os.fork)
    def _os_path_monkey_patch():
        # os.fork() is replaced with that
        _myself.on_before_fork()
        pid = os.fork()
        _myself.on_after_fork(pid == 0)  # on_after_fork(is_child::bool)
        return pid

    os.fork = _os_path_monkey_patch
