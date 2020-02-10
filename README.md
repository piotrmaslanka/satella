satella
========
[![Build Status](https://travis-ci.org/piotrmaslanka/satella.svg)](https://travis-ci.org/piotrmaslanka/satella)
[![Test Coverage](https://api.codeclimate.com/v1/badges/34b392b61482d98ad3f0/test_coverage)](https://codeclimate.com/github/piotrmaslanka/satella/test_coverage)
[![Code Climate](https://codeclimate.com/github/piotrmaslanka/satella/badges/gpa.svg)](https://codeclimate.com/github/piotrmaslanka/satella)
[![Issue Count](https://codeclimate.com/github/piotrmaslanka/satella/badges/issue_count.svg)](https://codeclimate.com/github/piotrmaslanka/satella)
[![PyPI](https://img.shields.io/pypi/pyversions/satella.svg)](https://pypi.python.org/pypi/satella)
[![PyPI version](https://badge.fury.io/py/satella.svg)](https://badge.fury.io/py/satella)
[![PyPI](https://img.shields.io/pypi/implementation/satella.svg)](https://pypi.python.org/pypi/satella)
[![Documentation Status](https://readthedocs.org/projects/satella/badge/?version=latest)](http://satella.readthedocs.io/en/latest/?badge=latest)

_satella.posix_ in unavailable on non-POSIX systems, but the rest should work OK.

Full [documentation](http://satella.readthedocs.io/en/latest/?badge=latest)
is available for the brave souls that do decide to use this library.

Satella is an almost-zero-requirements Python 3.5+ library for writing
server applications, especially those dealing with mundane but
useful things. It also runs on PyPy.

Satella contains, among other things:

* things to help you manage your [application's configuration](satella/configuration)
* a fully equipped [metrics library](satella/instrumentation/metrics)
* helpful [exception handlers](satella/exception_handling)
* common programming [idioms](satella/coding)

See [LICENSE](LICENSE) for text of the license. This library may contain
code taken from elsewhere on the internets, so this is copyright (c) respective authors.

