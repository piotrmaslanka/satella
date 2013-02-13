import sys
import os
import signal
import time

end = False

def __sighandler(a, b):
    global end
    end = True

def hang_until_sig(extra_signals=[]):
    """Will hang until this process receives SIGTERM or SIGINT.
    If you pass extra signal IDs (signal.SIG*) with extra_signals,
    then also on those signals this call will release."""
    global end

    signal.signal(signal.SIGTERM, __sighandler)
    signal.signal(signal.SIGINT, __sighandler)
    for s in extra_signals:
        signal.signal(s, __sighandler)
    
    while not end:
        try:
            signal.pause()
        except:         # pause() is undefined on Windows
            try:        # we will sleep for small periods of time
                time.sleep(0.5)
            except IOError:  # "Interrupted system call"
                pass

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