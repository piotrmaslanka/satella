# coding=UTF-8
"""
UNIX things
"""
from __future__ import print_function, absolute_import, division

import logging
import os

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
