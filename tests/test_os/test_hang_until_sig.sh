#!/bin/bash

python tests/test_posix/hang_until_sig.py &
kill -15 %1
wait
