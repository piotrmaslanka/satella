# v2.25.0

* added safe_listdir
* fixed a bug occurring in Python 3.10 with whereis

Build system
============

* Python 3.6 support dropped as it does not emply pyproject.toml, which is necessary
  to build this
* fixed unit tests to run on Py3.12
* removed Docker unit tests
