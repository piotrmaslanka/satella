#!/bin/bash

if [ $TRAVIS_BRANCH -eq 'master' ]; then
    pip install wheel twine
    python setup.py bdist bdist_wheel
    twine upload -u $PYPI_USER -p $PYPI_PWD dist/*
fi



