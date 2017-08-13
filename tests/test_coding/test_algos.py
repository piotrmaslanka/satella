# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import unittest
from satella.coding import merge_dicts


class TestMergeDicts(unittest.TestCase):
    def test_merge_dicts(self):

        tak = merge_dicts({'kupujemy': 'tak'}, {'kupujemy': 'nie'})
        nie = merge_dicts({'kupujemy': 'nie'}, {'kupujemy': 'tak'})

        self.assertEquals(tak['kupujemy'], 'nie')
        self.assertEquals(nie['kupujemy'], 'tak')

    def test_merge_lists(self):
        
        tak = merge_dicts({'kupujemy': ['tak']}, {'kupujemy': ['nie']})

        self.assertEqual(set(tak['kupujemy']), set(['tak', 'nie']))
