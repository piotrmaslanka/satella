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

    # Ascertain what Python are we working on. 2012 PyPy and earlier
    # may be affected by https://bugs.pypy.org/issue1255

    bugged_pypy = False
    try:
        import platform
    except:
        pass
    else:
        if platform.python_implementation() == 'PyPy':
            try:
                mon, day, year = platform.python_build()[1].split(' ')
                year = int(year)
            except:
                pass
            else:
                bugged_pypy = year <= 2012

    signal.signal(signal.SIGTERM, __sighandler)
    signal.signal(signal.SIGINT, __sighandler)
    for s in extra_signals:
        signal.signal(s, __sighandler)

    while not end:
        try:
            if bugged_pypy:
                time.sleep(1)   # see https://bugs.pypy.org/issue1255
            else:
                signal.pause()
        except:         # pause() is undefined on Windows
            try:        # we will sleep for small periods of time
                time.sleep(0.5)
            except IOError:  # "Interrupted system call"
                pass
    end = False     # fix a bug where subsequent calls to hang_until_sig would return automatically

def daemonize(uid=None, gid=None, redirect_stdouterr=True):
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

    if redirect_stdouterr:
        sys.stdout.close()
        sys.stderr.close()

        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
