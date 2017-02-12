# coding=UTF-8
"""
UNIX things
"""
from __future__ import print_function, absolute_import, division
import six
import logging
import os

from satella.unix.daemon import daemonize
from satella.unix.pidlock import AcquirePIDLock

__all__ = ('daemonize', 'AcquirePIDLock', 'is_running_as_root')


def is_running_as_root():
    """
    Is this process running as root?

    Checks whether EUID is 0
    :return: bool
    """
    return os.geteuid() == 0

