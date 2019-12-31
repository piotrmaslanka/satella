import os
import tempfile
import unittest

from satella.configuration.schema import *
from satella.configuration.sources import DirectorySource
from satella.exceptions import ConfigurationValidationError


class TestSchema(unittest.TestCase):

    def test_union(self):
        ps = Union(List(), Dict(keys=[create_key(String(), 'a')]))

        self.assertEquals(ps([1, 2, 3]), [1, 2, 3])
        self.assertEquals(ps({'a': 'b'}), {'a': 'b'})
        self.assertRaises(ConfigurationValidationError, lambda: ps(3))

    def test_descriptor_from_schema(self):
        schema = {
            "key_s": "str",
            "key_i": "int",
            "key_f": "float",
            "ip_addr": "ipv4",
            "nested": {
                "key_s": "str",
            },
            "default_five": {
                "type": "int",
                "default": 5
            },
            'logstash': {
                'type': 'list',
                'of': {
                    'host': 'str',
                    'port': {
                        'type': 'int',
                        'default': 9600,
                        'optional': True
                    }
                }
            },
            'boolean2': 'bool',
            'boolean': 'bool',
            'anything': 'any',
            "list": {
                "type": "list",
                "of": "str"
            },
            "unioned_list": {
                "type": "list",
                "of": {
                    "type": "union",
                    "of": [
                        {
                            "a": "str"
                        },
                        "int"
                    ]
                }}
        }

        s = descriptor_from_dict(schema)
        self.assertEquals(s({
            'key_s': 'string',
            'key_i': '5',
            'key_f': '5.5',
            'ip_addr': '10.2.3.43',
            'anything': 'any',
            'boolean': 'false',
            'unioned_list': [{"a": "a"}, 5],
            'nested': {
                'key_s': "string"
            },
            'boolean2': 0,
            'logstash': [
                {'host': 'ipv4'}
            ],
            'list': [1, 2, 3]
        }), {
            'key_s': 'string',
            'key_i': 5,
            'key_f': 5.5,
            'boolean': False,
            'ip_addr': '10.2.3.43',
            'anything': 'any',
            'boolean2': False,
            'unioned_list': [{"a": "a"}, 5],
            'nested': {
                'key_s': "string"
            },
            'logstash': [{'host': 'ipv4', 'port': 9600}],
            'list': ['1', '2', '3'],
            'default_five': 5
        })

    def test_schema(self):
        D1 = {
            'key_s': 'value',
            'key_i': '5',
            'key_f': '5.2',
            'unknown_key': None,
            'ip_addr': '127.0.0.1'
        }

        s = Dict([
            create_key(String(), 'key_s'),
            create_key(Integer(), 'key_i'),
            create_key(Float(), 'key_f'),
            create_key(String(), 'key_not_present', optional=True,
                       default='hello world'),
            create_key(IPv4(), 'ip_addr')
        ], unknown_key_mapper=lambda key, value: str(value))

        D2 = D1.copy()
        D2.update(key_not_present='hello world', key_i=5, key_f=5.2,
                  unknown_key='None')
        self.assertEqual(s(D1), D2)

    def test_schema_x(self):
        dir = tempfile.mkdtemp()

        with open(os.path.join(dir, 'smok5_config.json'), 'w') as f_out:
            f_out.write("""{
  "logging": {
    "logstash": {
      "host": "192.168.10.11",
      "port": 5959
    }
  }
}""")
        ds = DirectorySource(dir)
        print(ds.get_sources_from_directory(dir))
        source = ds.provide()

        schema = Dict([
            create_key(Dict([
                create_key(Dict([
                    create_key(String(), 'host'),
                    create_key(Integer(), 'port')
                ]), 'logstash')
            ]), 'logging')
        ])
        source = schema(source)