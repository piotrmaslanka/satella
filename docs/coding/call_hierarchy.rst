==============
Call hierarchy
==============

Satella enables you to define function call and their trees programmatically, so you can
for example express such a condition "call a function C with given args when either call of function A with given args or function B with given args returned True".

You can specify different argument sets for execution of such a tree, ie. you can provide different argument sets
and just tell your function to use the _i_-th one.

It additionally supports optional parallelization of function calls, if given an Executor.

.. autoclass:: satella.coding.call_hierarchy.Call
    :members:

.. autoclass:: satella.coding.call_hierarchy.CallWithArgumentSet
    :members:

.. autoclass:: satella.coding.call_hierarchy.CallIf
    :members:

.. autoclass:: satella.coding.call_hierarchy.Reduce
    :members:

.. autoclass:: satella.coding.call_hierarchy.ExecutionEnvironment
    :members:

You should run the callables in such a way

    ::

        def add(a, b):
            print(a+b)

        call_1 = CallWithArgumentSet(add, 0)
        ee = ExecutionEnvironment([((1, 2), {})])
        ee(call_1)

but in a pinch you can just type

    ::

        def add(a, b):
            print(a+b)

        call_1 = CallWithArgumentSet(add, 0)
        call_1(1, 2)

Note that you need to go through ExecutionEnvironment if you want to make use of parallelism.

.. autofunction:: satella.coding.call_hierarchy.call_with_ee

.. autofunction:: satella.coding.call_hierarchy.call

While inside such calls, you can use the following functions:

.. autofunction:: satella.coding.call_hierarchy.current_ee

.. autofunction:: satella.coding.call_hierarchy.current_call

.. autofunction:: satella.coding.call_hierarchy.current_args

.. autofunction:: satella.coding.call_hierarchy.current_kwargs

.. autofunction:: satella.coding.call_hierarchy.current_history

