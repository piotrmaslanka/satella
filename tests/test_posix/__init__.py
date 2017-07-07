# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import time
import logging
import unittest
import threading
import sys
import mock



class TestDaemon(unittest.TestCase):

    @unittest.skipIf('win' in sys.platform, 'Running on Windows')
    @mock.patch('sys.stdin')
    @mock.patch('sys.stdout')
    @mock.patch('sys.stderr')
    @mock.patch('os.fork')
    @mock.patch('os.umask')
    @mock.patch('os.setsid')
    @mock.patch('os.chdir')
    @mock.patch('sys.exit')
    def test_daemonize(self, stdin, stdout, stderr, fork, umask, setsid, chdir, exit):
        from satella.posix import daemonize

        daemonize()

        stdin.assert_called()
        stdout.assert_called()
        stderr.assert_called()
        fork.assert_called()
        umask.assert_called()
        chdir.assert_called_with('/')
        self.assertTrue(len(exit.mock_calls), 2)
