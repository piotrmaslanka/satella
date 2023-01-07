===================================
Welcome to satella's documentation!
===================================


Satella is an almost-zero-requirements Python 3.5+ library for writing
server applications. It has arisen out of my requirements to have some classes or design patterns handy, and kinda
wish-they-were-in-the-stdlib ones. especially those dealing with mundane but useful things. It also runs on PyPy, and
most of it runs on Windows (the part not dealing with forking processes, you see).

It's basically the stuff-I-wish-was-inside-Python-standard-library of piotrmaslanka_.

.. _piotrmaslanka: https://github.com/piotrmaslanka

Satella uses semantic_ versioning 2.0 for your convenience.

.. _semantic: https://semver.org/spec/v2.0.0.html

I believe you've already covered project's primary README at GitHub_. If not, please indulge.

.. _GitHub: https://github.com/piotrmaslanka/satella

.. toctree::
           :maxdepth: 2
           :caption: Contents

           configuration/schema
           configuration/sources
           coding/ctxt_managers
           coding/environment
           coding/functions
           coding/futures
           coding/structures
           coding/decorators
           coding/predicates
           coding/concurrent
           coding/sequences
           coding/transforms
           coding/typing
           debug/tainting
           instrumentation/cpu_time
           instrumentation/traceback
           instrumentation/memory
           instrumentation/metrics
           exception_handling
           dao
           db
           json
           posix
           import
           files
           random
           time
           exceptions
           processes
           cassandra
           opentracing


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
