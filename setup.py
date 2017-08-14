# coding=UTF-8
from setuptools import setup, find_packages

setup(name='satella',
      version='2.0.10',
      description=u'Utilities for writing servers in Python',
      author=u'Piotr Maślanka',
      author_email='piotrm@smok.co',
      keywords=['ha', 'high availability', 'scalable', 'scalability', 'server'],
      packages=find_packages(exclude=['tests.*', 'tests', 'examples.*', 'examples']),
      install_requires=[
            "six",
            "monotonic",
            "backports.typing"
      ],
      tests_require=[
          "nose", "mock", "coverage"
      ],
      test_suite='nose.collector',
      classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Operating System :: POSIX',
            'Operating System :: OS Independent',
            'Development Status :: 2 - Pre-Alpha',
            'License :: OSI Approved :: MIT License',
            'Topic :: Software Development :: Libraries'

      ]
    )
