import unittest
import typing as tp
import logging
from satella.instrumentation.metrics.json import update, annotate_every_leaf_node_with_labels, \
    are_equal

logger = logging.getLogger(__name__)


class TestJson(unittest.TestCase):
    def test_update(self):
        a1 = {'root': {'metric': [{'period': 1, '_': 25.0}, {'period': 2, '_': 50.0}]}}
        a2 = {'root': {'metric': [{'period': 1, '_': 20.0}]}}
        a3 = update(a1, a2)
        a4 = {'root': {'metric': [{'period': 1, '_': 20.0}, {'period': 2, '_': 50.0}]}}
        self.assertEqual(a3, a4)

    def test_are_equal(self):
        a = {'root': {'_': {'_': 5, 'sum': {'_': 5, '_timestamp': 10}}}}
        b = {'root': {'_': {'_': 6, 'sum': {'_': 7, '_timestamp': 12}}}}
        self.assertEqual({'root': {'_': {'_': 6, 'sum': {'_': 7, '_timestamp': 12}}}}, update(a, b))

    def test_update_3(self):
        a = { 'mhc': {   '_timestamp': 1580953411.8270154,
               'submissions_per_second': [   {   '_': 0,
                                                 '_timestamp': 1580953523.7159278,
                                                 'period': 1,
                                                 'service': 'mhc',
                                                 'slot': 1},
                                             {   '_': 0,
                                                 '_timestamp': 1580953411.8270352,
                                                 'period': 20,
                                                 'service': 'mhc',
                                                 'slot': 1},
                                             {   '_': 7,
                                                 '_timestamp': 1580953523.7159278,
                                                 'period': 60,
                                                 'service': 'mhc',
                                                 'slot': 1},
                                             ]}}

        b = { 'mhc': {   '_timestamp': 1580953411.8270154,
               'submissions_per_second': [  {
                                                '_': 3,
                                                 '_timestamp': 1580953463.6468315,
                                                 'period': 1,
                                                 'service': 'mhc',
                                                 'slot': 1},
                                             {   '_': 5,
                                                 '_timestamp': 1580953463.6468315,
                                                 'period': 20,
                                                 'service': 'mhc',
                                                 'slot': 1},
                                               {'_': 4,
                                                '_timestamp': 1580953463.6468315,
                                                'period': 60,
                                                'service': 'mhc',
                                                'slot': 1},
                                           ]}}
        self.assertEqual(b, update(a, b))

    def test_update_2(self):
        a = {'root': {'_': [{'a': 5, "_": 3}], 'sum': [{"a": 5, "_": 3}]}}
        b = {'root': {'_': [{'a': 5, "_": 7}], 'sum': [{"a": 3, "_": 8}]}}
        c = update(a, b)
        self.assertEqual({'root': {'_': [{'a': 5, "_": 7}], 'sum': [{"a": 5, "_": 3},
                                                                    {"a": 3, "_": 8}]}}, c)

    def test_annotate(self):
        a = {'root': {'metric': [{'period': 1, '_': 25.0}, {'period': 2, '_': 50.0}]}}
        b = annotate_every_leaf_node_with_labels(a, {'key': 'value'})
        self.assertEqual({'root': {'metric': [{'period': 1, '_': 25.0,
                                               'key': 'value'}, {'period': 2, '_': 50.0,
                                                                 'key': 'value'}]}}, b)

    def test_annotate_timestamp(self):
        a = {'_timestamp': 2342342342.25, '_': [{'_': 5}, {'_': 6}], 'k': 3}
        b = annotate_every_leaf_node_with_labels(a, {'key': 'value'})
        self.assertEqual({'_timestamp': 2342342342.25, '_': [{'_': 5, 'key': 'value'},
                                                             {'_': 6, 'key': 'value'}],
                          'k': 3}, b)
