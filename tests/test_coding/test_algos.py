# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import unittest
from satella.coding import merge_dicts


class TestMergeDicts(unittest.TestCase):


    def test_lolwut(self):
        with open('lolwut', 'wb') as fout:
            fout.write(b'{"a":2}')



    def test_merge_dicts(self):

        tak = merge_dicts({'kupujemy': 'tak'}, {'kupujemy': 'nie'})
        nie = merge_dicts({'kupujemy': 'nie'}, {'kupujemy': 'tak'})

        self.assertEquals(tak['kupujemy'], 'nie')
        self.assertEquals(nie['kupujemy'], 'tak')

    def test_merge_lists(self):
        
        tak = merge_dicts({'kupujemy': ['tak']}, {'kupujemy': ['nie']})

        self.assertEqual(set(tak['kupujemy']), set(['tak', 'nie']))

    def test_bugA(self):
        tak = merge_dicts({}, {"a": "b"})
        self.assertEqual(tak['a'], 'b')

    def test_adds(self):
        tak = merge_dicts({'kupujemy': 'tak'}, {'xupujemy': 'nie'})

        self.assertEquals(tak['xupujemy'], 'nie')
        self.assertEquals(tak['kupujemy'], 'tak')

    def test_nest(self):
        tak = merge_dicts({'kupujemy': {"y": ['tak']}},
                          {'kupujemy': {"y": ['nie']}})

        q = tak['kupujemy']['y']

        self.assertIn('tak', q)
        self.assertIn('nie', q)
