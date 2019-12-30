from satella.configuration.sources import load_source_from_dict, load_source_from_list
from .test_sources.utils import SourceTestCase

INNER_DATA = [
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

DICT_DATA = {
    'type': 'MergingSource',
    'args': INNER_DATA
}


class TestLoadSourceFromDict(SourceTestCase):
    def test_lsf(self):
        output = {'a': 5, 'b': 5, 'c': 21}
        self.assertSourceHas(load_source_from_dict(DICT_DATA), output)
        self.assertSourceHas(load_source_from_list(INNER_DATA), output)
