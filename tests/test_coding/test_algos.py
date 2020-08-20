import os
import unittest

from satella.coding import merge_dicts, update_attr_if_none


class TestMergeDicts(unittest.TestCase):
    def test_update_attr_if_none(self):
        class Object:
            def __init__(self):
                self.a = None
                self.b = 5

        a = Object()
        update_attr_if_none(a, 'a', 5)
        self.assertEqual(a.a, 5)
        update_attr_if_none(a, 'b', 4)
        update_attr_if_none(a, 'c', 8)
        self.assertEqual(a.b, 5)
        self.assertRaises(AttributeError, lambda: update_attr_if_none(
            a, 'd', 6, on_attribute_error=False))
        update_attr_if_none(a, 'b', 6, if_value_is_not_none=True)
        self.assertEqual(a.b, 6)
        self.assertEqual(a.c, 8)

    def test_advanced_merge_dicts(self):

        DA = {
            "google-fcm": {
                "http-auth": {
                    "digicort": "key=digi",
                },
                "endpoint": "https://fcm.googleapis.com/fcm/send"
            }
        }

        DB = {
            "google-fcm": {
                "http-auth": {
                    "springblade": "key=spri"
                },
                "endpoint": "https://fcm.googleapis.com/fcm/send"
            }
        }

        DC = merge_dicts(DA, DB)

        self.assertEqual(DC['google-fcm']['http-auth']['digicort'], 'key=digi')
        self.assertEqual(DC['google-fcm']['http-auth']['springblade'], 'key=spri')
        self.assertEqual(DC['google-fcm']['endpoint'], 'https://fcm.googleapis.com/fcm/send')

    def test_merge_dicts(self):

        tak = merge_dicts({'kupujemy': 'tak'}, {'kupujemy': 'nie'})
        nie = merge_dicts({'kupujemy': 'nie'}, {'kupujemy': 'tak'})

        self.assertEqual(tak['kupujemy'], 'nie')
        self.assertEqual(nie['kupujemy'], 'tak')

    def test_merge_lists(self):

        tak = merge_dicts({'kupujemy': ['tak']}, {'kupujemy': ['nie']})

        self.assertEqual(set(tak['kupujemy']), set(['tak', 'nie']))

    def test_bugA(self):
        tak = merge_dicts({}, {"a": "b"})
        self.assertEqual(tak['a'], 'b')

    def test_adds(self):
        tak = merge_dicts({'kupujemy': 'tak'}, {'xupujemy': 'nie'})

        self.assertEqual(tak['xupujemy'], 'nie')
        self.assertEqual(tak['kupujemy'], 'tak')

    def test_nest(self):
        tak = merge_dicts({'kupujemy': {"y": ['tak']}},
                          {'kupujemy': {"y": ['nie']}})

        q = tak['kupujemy']['y']

        self.assertIn('tak', q)
        self.assertIn('nie', q)
