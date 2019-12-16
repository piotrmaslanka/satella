import unittest
import typing as tp
from satella.json import JSONAble, json_encode


class TestJson(unittest.TestCase):

    def test_jsonable_objects(self):

        class MyClass(JSONAble):
            def to_json(self) -> tp.Union[list, dict, str, int, float, None]:
                return []

        self.assertEquals(json_encode(MyClass()), '[]')

    def test_unjsonable_objects(self):
        class MyClass:
            pass

        self.assertRaises(TypeError, lambda: json_encode(MyClass()))
