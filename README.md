satella
========
[![PyPI](https://img.shields.io/pypi/pyversions/satella.svg)](https://pypi.python.org/pypi/satella)
[![PyPI version](https://badge.fury.io/py/satella.svg)](https://badge.fury.io/py/satella)
[![PyPI](https://img.shields.io/pypi/implementation/satella.svg)](https://pypi.python.org/pypi/satella)
[![Documentation Status](https://readthedocs.org/projects/satella/badge/?version=latest)](http://satella.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/pypi/l/satella)](https://github.com/piotrmaslanka/satella)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

Important!
----------

Development has been moved to [external PyPI](https://git.dms-serwis.com.pl/smokserwis/satella).
In order to install latest Satella just type:

```
pip install --extra-index-url https://git.dms-serwis.com.pl/api/v4/groups/330/-/packages/pypi/simple satella
```

If you want to put it in requirements.txt just type:

```
--extra-index-url https://git.dms-serwis.com.pl/api/v4/groups/330/-/packages/pypi/simple
satella
nose2
coverage
```

It's still free, MIT-licensed and publicly available. No one's taking it from you :)

**I'll try to submit the builds to regular [PyPI](https://pypi.org/project/satella/) as well!!**


What is Satella?
----------------

Satella is an almost-zero-requirements Python 3.7+ library for writing server applications. It has arisen out of my
requirements to have some classes or design patterns handy, and kinda wish-they-were-in-the-stdlib ones. especially
those dealing with mundane but useful things. It also runs on PyPy, and most of it runs on Windows (the part not dealing
with forking processes, you see).

Satella uses [semantic versioning 2.0](https://semver.org/spec/v2.0.0.html).

Satella contains, among other things:

* things to help you manage your [application's configuration](satella/configuration) that allows
    you to both load a configuration and specify it's schema using only
    Python dictionaries
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
* helpful [exception handlers](satella/exception_handling) as well as capacity to dump all stack frames
    along with their local variables for each thread
* monitoring [CPU usage](satella/instrumentation/cpu_time/collectors) on the system and by your own process
* common programming [idioms and structures](satella/coding)

Most Satella objects make heavy use of `__slots__`, so they are memory friendly and usable on embedded systems, where
memory is at premium.

Change log is kept as part of [old release notes](https://github.com/piotrmaslanka/satella/releases),
new [CHANGELOG.md](CHANGELOG.md) is to remain for all posteriority.

Full [documentation](http://smokserwis.docs.smok.co/satella)
is available for the brave souls that do decide to use this library.

See [LICENSE](LICENSE) for text of the license. This library may contain code taken from elsewhere on the internets, so
this is copyright (c) respective authors.

If you want to install extra modules, just run

Installation
------------

```bash
pip install --extra-index-url https://git.dms-serwis.com.pl/api/v4/groups/330/-/packages/pypi/simple satella
```

Running unit tests
------------------

Tests run by default on local CI/CD.

They should pass on Windows too, but some tests requiring POSIX-like functionality are skipped.

Automatic release system
------------------------

Releases happen automatically. Just add a tag with the name of the version.

**NOTE that changes from 2.25 will be numbered as tags without the prefix ```v```**!
