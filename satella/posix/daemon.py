# coding=UTF-8
from __future__ import print_function, absolute_import, division

import logging
import os
import sys
import six

try:
    import pwd
    import grp
except ImportError:
    pass    # Windows?

from satella.coding import typed, Callable

logger = logging.getLogger(__name__)


def _redirect_descriptors_to_null():
    sys.stdin = open('/dev/null', 'rb')
    sys.stdout = open('/dev/null', 'wb')
    sys.stderr = open('/dev/null', 'wb')

def _close_descriptors():
    for d in [sys.stdin, sys.stdout, sys.stderr]:
        d.close()

def _double_fork(exit_via):
    os.umask(0)

    if os.fork() > 0:
        exit_via()  # parent exits

    os.setsid()

    if os.fork() > 0:
        exit_via()  # parent exits
    os.chdir('/')

@typed(Callable, bool, (None, int), (None, int))
def daemonize(exit_via=sys.exit,
              redirect_std_to_devnull=True,
              uid=None, gid=None):
    """
    Make this process into a daemon.

    This entails:

    - umask 0
    - forks twice
    - be the child of init
    - becomes session leader
    - changes root directory to /
    - closes stdin, stdout, stderr
    - (option) redirects stdin, stdout, stderr to /dev/null

    Refer - "Advanced Programming in the UNIX Environment" 13.3

    :param exit_via: callable used to terminate process
    :param redirect_std_to_devnull: whether to redirect stdin, stdout and stderr to /dev/null
    :param uid: User to set (via seteuid). Default - this won't be done. You can pass either user name as string or UID.
    :param gid: Same as UID, but for groups. These will be resolved too.
    :raises KeyError: uid/gid was passed as string, but getpwnam() failed
    """

    _double_fork(exit_via=exit_via)
    _close_descriptors()

    if redirect_std_to_devnull:
        _redirect_descriptors_to_null()

    if uid is not None:
        if isinstance(uid, six.string_types):
            uid = pwd.getpwnam(uid).pw_uid  # raises KeyError

        os.seteuid(uid)

    if gid is not None:
        if isinstance(uid, six.string_types):
            gid = grp.getpwnam(uid).gr_gid  # raises KeyError

        os.setegid(gid)
