# debug module

debug module is used during development. If Python's \_\_debug__ variable is set,
debug functions become operational. 

If it's not (Python was launched with -O), they will do their best not to affect
performance, including removing themselves from code.

## Type checking

```python
from satella.coding.debug import typed

@typed(int, int)
def add_two_numbers(a, b):
    return a+b
```

If you want to check for None-ness, you can pass None as well. Types for particular
arguments can also be tuples or lists, in that case if any of these types matches, 
it's OK.

If you don't want to check a particular argument for type, pass None as type. 
Conversely, to check for being None, pass (None, ).

If type check fails, TypeError will be raised.
