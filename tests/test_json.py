import json
import typing as tp
import unittest

from satella.json import JSONAble, json_encode, read_json_from_file, write_json_to_file, \
write_json_to_file_if_different


class TestJson(unittest.TestCase):

    def test_write_json_to_file_if_different(self):
        d = {'test': 4}
        self.assertTrue(write_json_to_file_if_different('test2.json', d))
        self.assertFalse(write_json_to_file_if_different('test2.json', d))
        d = {'test': 5}
        self.assertTrue(write_json_to_file_if_different('test2.json', d))
        self.assertFalse(write_json_to_file_if_different('test2.json', d))

    def test_load_json_from_file(self):
        d = {'test': 2}
        write_json_to_file('test.json', d)
        self.assertEqual(read_json_from_file('test.json'), d)

    def test_jsonable_objects(self):
        class MyClass(JSONAble):
            def to_json(self) -> tp.Union[list, dict, str, int, float, None]:
                return []

        self.assertEqual(json_encode(MyClass()), '[]')

    def test_unjsonable_objects(self):
        class MyClass:
            def __init__(self, a):
                self.a = a

        data = json.loads(json_encode(MyClass(5)))
        self.assertEqual(data['a'], '5')

        class MyClass2:
            __slots__ = ('a', )

            def __init__(self, a):
                self.a = a

        data = json.loads(json_encode(MyClass2(5)))
        self.assertEqual(data['a'], 5)
