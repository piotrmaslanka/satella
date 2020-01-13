import os
import unittest

from satella.coding import merge_dicts


class TestMergeDicts(unittest.TestCase):
    def test_lolwut(self):
        try:
            with open('lolwut', 'wb') as fout:
                fout.write(b'{"a":2}')
        finally:
            os.unlink('lolwut')

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
