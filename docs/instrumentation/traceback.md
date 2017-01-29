# Traceback

_Traceback_ object is used to preserve all the information you can get
in case of an exception. It preserves:
* Information about all stack frames in this thread
* Every local and global variable at every stack frame
    * If the variable is pickable, it is pickled on the spot
    * Variable's _repr_ is always preserved
    * Of course variable name is saved
    
It also allows to pretty print the exception. Traceback is picklable, so you 
can safely do so and analyze the exception at your own leisure.

Usage:
```python
from satella.instrumentation import Traceback

try:
    ...
except:
    tb = Traceback()
    
    print(tb.pretty_print())    # print stack trace
    
    tb_p = tb.pickle()  # pickles the traceback
```

_Traceback_ should be created in the exception it is supposed to capture,
as it captures exception info from _sys.exc_info()_.