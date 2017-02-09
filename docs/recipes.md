# Recipes

How to do common things.


## Acquire a PID lock file

Use a context manager, _AcquirePIDLock_ from module _satella.pid_. Example:

Example:
```python
from satella.pidlock import AcquirePIDLock

with AcquirePIDLock('satella.pid'):
    print('Lock is acquired!')
    
print('Now lock is acquired!')
```

_AcquirePIDLock_ accepts extra keyword parameters:
* base_dir (default _/var/run_) - base directory of PID lock files
* delete_on_dead (default False) - if lock exists, but it's holder is dead, 
 remove the lock file and retry.
 
Entering _AcquirePIDLock_ context may throw:

* _AcquirePIDLock.FailedToAcquire_ - base class for errors. Thrown if can't read the file
* _AcquirePIDLock.LockIsHeld_ - lock is already held. This has two attributes - pid (int), the PID of holder,
 and is_alive (bool) - whether the holder is an alive process



Writing to _/var/run_ may require root permissions.
