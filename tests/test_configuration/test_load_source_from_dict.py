import enum
import os

from satella.configuration.sources import load_source_from_dict, load_source_from_list
from .test_sources.utils import SourceTestCase

INNER_DATA = [
    {
        'type': 'BuildObjectFrom',
        'key': 'test',
        'child': {
            'type': 'StaticSource',
            'args': [
                {
                    "a": 5
                }
            ]
        }
    },
    {
        'type': 'JSONSource',
        'arg': '{"d": 10}'
    },
    {
        'type': 'JSONSource',
        'args': ['{"a": 5}']
    },
    {
        'type': 'JSONSource',
        'args': ['ivnadsgfgsfg'],
        'optional': True
    },
    {
        'type': 'JSONSource',
        'args': ['{"b": 5}']
    },
    {
        'type': 'JSONSource',
        'encoding': "base64",
        'args': [
            {
                'type': 'binary',
                'value': 'eyJjIjogMjF9\n',
            }
        ]
    }
]

INNER_DATA_2 = {
    'type': 'EnvironmentSource',
    'args': [
        'TEST_ENV', 'TEST_ENV'
    ],
    'cast_to': {
        'type': 'import',
        'module': 'tests.test_configuration.test_load_source_from_dict',
        'attribute': 'MyEnum',
        'cast_before': {
            'type': 'lambda',
            'operation': 'int(x)'
        }
    }
}


class MyEnum(enum.IntEnum):
    A = 0

DICT_DATA = {
    'type': 'MergingSource',
    'args': INNER_DATA
}


class TestLoadSourceFromDict(SourceTestCase):
    def test_lsf(self):
        output = {'a': 5, 'b': 5, 'c': 21, 'test': {'a': 5}, 'd': 10}
        self.assertSourceHas(load_source_from_dict(DICT_DATA), output)
        self.assertSourceHas(load_source_from_list(INNER_DATA), output)

    def test_env(self):
        os.environ['TEST_ENV'] = '0'
        source = load_source_from_dict(INNER_DATA_2).provide()
        self.assertEqual(source['TEST_ENV'], MyEnum(0))
