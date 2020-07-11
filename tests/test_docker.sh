#!/bin/bash
set -e

coverage run --parallel-mode -m nose2 -vv
coverage combine
coverage report
