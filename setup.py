# coding=UTF-8
from setuptools import setup

setup(name='satella',
      version='1.9.0',
      description=u'Utilities for writing servers in Python',
      author=u'Piotr Maślanka',
      author_email='piotrm@smok.co',
      keywords=['ha', 'high availability', 'scalable', 'scalability', 'server'],
      packages=[
            'satella',
      ],
      install_requires=[
            "six",
            "monotonic",
      ],
      tests_require=[
          "nose"
      ],
      test_suite='nose.collector',
      classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Operating System :: POSIX',
            'Development Status :: 1 - Planning',
            'License :: OSI Approved :: MIT License',
            'Topic :: Software Development :: Libraries'

      ]
    )
