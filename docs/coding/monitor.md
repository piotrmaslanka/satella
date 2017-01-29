# Monitor

A monitor is a Java-like synchronization idea. Inheriting from _Monitor_ outfits the class with a Lock
(or a reentrant lock, if _RMonitor_ is used), that can be used to coordinate access to some shared resource.

Take care to invoke _Monitor's_ constructor when inheriting, or this won't work.

You can decorate your methods with _Monitor.synchronized_ to have them execute with the lock acquired. 
If you have such a method, you can also temporarily release the lock using context manager  _Monitor.release_
(it will be reacquired) when context manager is exited.
 
You can also use manual synchronization with context manager _Monitor.acquire_. 

```python
from satella.coding import Monitor


class MyProtectedClass(Monitor):
    def __init__(self, *args):
        super(Monitor, self).__init__()
         
    @Monitor.synchronized
    def synchronized(self):
        pass # everything here is executed with class lock acquired
        
    @Monitor.synchronized
    def temporary_release(self):
        pass    # lock is acquired here
        with Monitor.release(self):
            pass    # lock is NOT ACQUIRED here
        pass # and here it's reacquired again
        
    def manual_sync(self):
        pass    # not synchronized
        with Monitor.acquire(self):
            pass # synchronized        
    
```

You can also use _Monitor.release_ and _Monitor.acquire_ with other objects than self, but exercise 
caution and think over the consequences.
    
