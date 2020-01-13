#!/bin/bash

set -x
set -e

if [ ! -z "$TRAVIS_TAG" ]; then
    pip install wheel twine
    python setup.py bdist bdist_wheel
    twine upload -u $PYPI_USER -p $PYPI_PWD dist/*
fi
