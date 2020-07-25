from setuptools import setup, find_packages
import unittest
from satella import __version__


setup(keywords=['ha', 'high availability', 'scalable', 'scalability', 'server', 'metrics'],
      packages=find_packages(include=['satella', 'satella.*']),
      version=__version__,
      install_requires=[
            'psutil'
      ],
      test_suite='nose2.collector.collector',
      python_requires='!=2.7.*,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
      extras_require={
            'HTTPJSONSource': ['requests'],
            'YAMLSource': ['pyyaml'],
            'TOMLSource': ['toml'],
            'Faster JSONSource': ['ujson'],
            'satella.cassandra': ['cassandra-driver']
      }
      )
