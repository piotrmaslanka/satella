# coding=UTF-8
from __future__ import print_function, absolute_import, division

import multiprocessing
import os
import sys
import unittest

from mock import patch, Mock

from satella.posix import PIDFileLock, LockIsHeld


def acquire_lock_file_and_wait_for_signal(q, p):
    with PIDFileLock('lock', '.'):
        p.put(None)
        q.get()


class TestPidlock(unittest.TestCase):

    def test_pidlock(self):
        with PIDFileLock('lock', '.'):
            self.assertTrue(os.path.exists('./lock'))
            r = open('./lock', 'rb').read()
            try:
                r = int(r)
            except ValueError:
                return  # lol wut
            self.assertEquals(int(r), os.getpid())

        self.assertTrue(not os.path.exists('./lock'))

    def test_pidlock_multiacquire(self):
        q, p = multiprocessing.Queue(), multiprocessing.Queue()
        process = multiprocessing.Process(target=acquire_lock_file_and_wait_for_signal, args=(q, p))
        process.start()
        p.get()
        n = PIDFileLock('lock', '.')
        try:
            self.assertRaises(LockIsHeld, lambda: n.acquire())
        finally:
            q.put(None)
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
