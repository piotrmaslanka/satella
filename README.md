satella
========
[![Build Status](https://circleci.com/gh/piotrmaslanka/satella.svg?style=svg)](https://app.circleci.com/pipelines/github/piotrmaslanka/satella)
[![Test Coverage](https://api.codeclimate.com/v1/badges/34b392b61482d98ad3f0/test_coverage)](https://codeclimate.com/github/piotrmaslanka/satella/test_coverage)
[![Code Climate](https://codeclimate.com/github/piotrmaslanka/satella/badges/gpa.svg)](https://codeclimate.com/github/piotrmaslanka/satella)
[![Issue Count](https://codeclimate.com/github/piotrmaslanka/satella/badges/issue_count.svg)](https://codeclimate.com/github/piotrmaslanka/satella)
[![PyPI](https://img.shields.io/pypi/pyversions/satella.svg)](https://pypi.python.org/pypi/satella)
[![PyPI version](https://badge.fury.io/py/satella.svg)](https://badge.fury.io/py/satella)
[![PyPI](https://img.shields.io/pypi/implementation/satella.svg)](https://pypi.python.org/pypi/satella)
[![Documentation Status](https://readthedocs.org/projects/satella/badge/?version=latest)](http://satella.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/pypi/l/satella)](https://github.com/piotrmaslanka/satella)

Satella is an almost-zero-requirements Python 3.5+ library for writing
server applications. It has arisen out of my requirements to have some classes or design patterns handy, and kinda
wish-they-were-in-the-stdlib ones. especially those dealing with mundane but useful things. It also runs on PyPy, and
most of it runs on Windows (the part not dealing with forking processes, you see).

Satella uses [semantic versioning 2.0](https://semver.org/spec/v2.0.0.html).

Satella contains, among other things:
 
* things to help you manage your [application's configuration](satella/configuration)
* a fully equipped [metrics library](satella/instrumentation/metrics)
    * alongside a fully metricized [ThreadPoolExecutor](satella/instrumentation/metrics/structures/threadpool.py)
    * and an exporter to [Prometheus](satella/instrumentation/metrics/exporters/prometheus.py) or really any 
      [OpenMetrics](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md) compliant
      ingester
    * as well as exporters/metricizers for the following libraries:
      * [AWS](https://github.com/piotrmaslanka/aws-satella)
      * [FastAPI](https://github.com/Dronehub/fastapi-satella-metrics)
      * [Django](https://github.com/piotrmaslanka/django-satella-metrics)
      * [Flask](https://github.com/piotrmaslanka/flask-satella-metrics)
* helpful [exception handlers](satella/exception_handling) 
* common programming [idioms and structures](satella/coding)

Most Satella objects make heavy use of `__slots__`, so they are memory friendly and usable on
embedded systems, where memory is at premium.

Change log is kept as part of [release notes](https://github.com/piotrmaslanka/satella/releases).
The [CHANGELOG.md](CHANGELOG.md) file is only to track changes since last release.

Full [documentation](http://satella.readthedocs.io/en/latest/?badge=latest)
is available for the brave souls that do decide to use this library.

See [LICENSE](LICENSE) for text of the license. This library may contain
code taken from elsewhere on the internets, so this is copyright (c) respective authors.

# Running unit tests

Tests run by default on CircleCI. 
Just build and run the attached 
[Dockerfile](Dockerfile). 
These tests run on Python 3.8

They pass on Windows too, but some tests 
requiring POSIX-like functionality are skipped.
