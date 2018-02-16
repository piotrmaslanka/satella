# coding=UTF-8
from setuptools import setup, find_packages

setup(keywords=['ha', 'high availability', 'scalable', 'scalability', 'server'],
      packages=find_packages(include=['satella', 'satella.*']),
      install_requires=[
          "six",
          "monotonic",
          "typing"
      ],
      tests_require=[
          "nose", "mock", "coverage"
      ],
      test_suite='nose.collector',
      python_requires='>=2.7.*,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*'
      )
