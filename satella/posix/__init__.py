# coding=UTF-8
"""
UNIX things
"""
from __future__ import print_function, absolute_import, division
import six
import logging
import os
import warnings

try:
    from satella.posix.daemon import daemonize
    from satella.posix.pidlock import AcquirePIDLock


    def is_running_as_root():
        """
        Is this process running as root?

        Checks whether EUID is 0
        :return: bool
        """
        return os.geteuid() == 0


except ImportError:
    warnings.warn(u'Not running on POSIX, some functionality is unavailable')




