import sys
import os

def daemonize():
    """On POSIX-compatible systems, make the current process a daemon
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