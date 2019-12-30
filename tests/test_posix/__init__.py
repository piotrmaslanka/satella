# coding=UTF-8
from __future__ import print_function, absolute_import, division

import multiprocessing
import os
import sys
import time
import unittest

from mock import patch, Mock

from satella.posix import AcquirePIDLock, LockIsHeld, hang_until_sig


def acquire_lock_file_and_wait_for_signal():
    with AcquirePIDLock('lock', '.'):
        hang_until_sig()


class TestPidlock(unittest.TestCase):

    def test_pidlock(self):
        with AcquirePIDLock('lock', '.'):
            self.assertTrue(os.path.exists('./lock'))
            r = open('./lock', 'rb').read()
            try:
                r = int(r)
            except ValueError:
                return  # lol wut
            self.assertEquals(int(r), os.getpid())

        self.assertTrue(not os.path.exists('./lock'))

    def test_pidlock_multiacquire(self):
        process = multiprocessing.Process(target=acquire_lock_file_and_wait_for_signal)
        process.start()
        time.sleep(1)
        n = AcquirePIDLock('lock', '.')
        try:
            self.assertRaises(LockIsHeld, lambda: n.acquire())
        finally:
            process.terminate()
            process.join()


class TestDaemon(unittest.TestCase):
    @unittest.skipIf('win' in sys.platform, 'Running on Windows')
    def test_daemonize(self):
        with patch('sys.stdin') as stdin, patch('sys.stdout') as stdout, patch(
                'sys.stderr') as stderr, \
                patch('os.fork', return_value=0) as fork, patch('os.umask') as umask, patch(
            'os.setsid') as setsid, \
                patch('os.chdir') as chdir, patch('sys.exit', new=lambda: 0) as exit:
            from satella.posix import daemonize

            stdin.close, stdout.close, stderr.close = Mock(), Mock(), Mock()

            daemonize()

            stdin.close.assert_called()
            stdout.close.assert_called()
            stderr.close.assert_called()
            fork.assert_called()
            setsid.assert_called()
            umask.assert_called_with(0)
            chdir.assert_called_with('/')
