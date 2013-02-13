import sys
import os

def daemonize(uid=None, gid=None):
    """On POSIX-compatible systems, make the current process a daemon.
    Additionally drops privileges, switching to user uid and group gid.
    No-op on Windows"""
    if sys.platform == 'win32': return

    try:
         if os.fork() > 0: sys.exit(0)
    except OSError:
         sys.exit(1)

    os.chdir("/")
    os.setsid()
    os.umask(0)

    try:
        if os.fork() > 0: sys.exit(0)
    except OSError:
         sys.exit(1)

    if uid != None:
        os.setuid(uid)

    if gid != None:
        os.setgid(gid)