satella
========
[![Build Status](https://travis-ci.org/piotrmaslanka/satella.svg)](https://travis-ci.org/piotrmaslanka/satella)
[![Code Climate](https://codeclimate.com/github/piotrmaslanka/satella/badges/gpa.svg)](https://codeclimate.com/github/piotrmaslanka/satella)
[![Test Coverage](https://codeclimate.com/github/piotrmaslanka/satella/badges/coverage.svg)](https://codeclimate.com/github/piotrmaslanka/satella/coverage)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)]()
[![PyPI](https://img.shields.io/pypi/pyversions/satella.svg)]()
[![PyPI](https://img.shields.io/pypi/implementation/satella.svg)]()

**satella is currently undergoing a major rework. See branch satella2 for details.
This WILL break compatibility.**

**satella 1.0 remain in maintenance mode**

Satella is a Python library for writing server applications, especially those dealing with
small network-oriented tasks. Over time it will constitute a reasonably large library with useful things.

Satella abstracts away communication links a "channels". Channels can be blocking, nonblocking, multiplexed - used as the user likes it. They are essentially streams with rich read functionality and fail awareness. Channels follow an unified API, which makes them simple to understand.

Satella is easy-to-use. It's main task is to reduce the cognitive load on the programmer. It requires minimum-to-none startup and faciliates it's objects, classes and procedures to be used without requiring the coder to read and understand multitude information about unnecessary far-away classes. Code written is simple and concise.

Satella runs both on PyPy and CPython 2.7

See LICENSE for text of the license.