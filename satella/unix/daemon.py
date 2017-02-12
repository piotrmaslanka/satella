# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import os
import sys
import warnings
import pwd
import grp

logger = logging.getLogger(__name__)


def daemonize(exit_via=sys.exit,
              redirect_std_to_devnull=True,
              uid=None, gid=None,
              yes_i_know_running_as_root_is_not_safe=False):
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
    :param yes_i_know_running_as_root_is_not_safe: set to True to silence warnings stemming from not providing uid and gid
    :raises KeyError: uid/gid was passed as string, but getpwnam() failed
    """

    os.umask(0)

    if os.fork() > 0:
        exit_via()  # parent exits

    os.setsid()

    if os.fork() > 0:
        exit_via()  # parent exits

    os.chdir('/')

    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()

    if redirect_std_to_devnull:
        sys.stdin = open('/dev/null', 'rb')
        sys.stdout = open('/dev/null', 'wb')
        sys.stderr = open('/dev/null', 'wb')


    if uid is not None:
        if isinstance(uid, six.string_types):
            uid = pwd.getpwnam(uid).pw_uid # raises KeyError

        os.seteuid(uid)

    if gid is not None:
        if isinstance(uid, six.string_types):
            gid = grp.getpwnam(uid).gr_gid # raises KeyError

        os.setegid(gid)

    if ((uid is None) or (gid is None)) and (not yes_i_know_running_as_root_is_not_safe):
        warnings.warn(u"Not changing user and group is not a good idea. Hope you know what you''re doing")

    if yes_i_know_running_as_root_is_not_safe:  #todo should it be here?
        warnings.warn(u"Unstable feature used")

