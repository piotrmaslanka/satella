# coding=UTF-8
from __future__ import print_function, absolute_import, division
import os
import unittest
from satella.posix import suicide


class TestSuicide(unittest.TestCase):

    def test_suicide(self):
        pcid = os.fork()

        if pcid == 0:
            suicide()

        self.assertEqual(os.wait(), (pcid, 9))
