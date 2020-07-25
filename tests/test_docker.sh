#!/bin/bash
set -e

nose2 -vv
coverage report
