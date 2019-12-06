# coding=UTF-8
from setuptools import setup, find_packages
from satella import __version__

setup(keywords=['ha', 'high availability', 'scalable', 'scalability', 'server'],
      packages=find_packages(include=['satella', 'satella.*']),
      version=__version__,
      install_requires=[
      ],
      tests_require=[
          "nose", "mock", "coverage"
      ],
      test_suite='nose.collector',
      python_requires='!=2.7.*,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*'
      )
