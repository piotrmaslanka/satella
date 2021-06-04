from setuptools import setup, find_packages
from satella import __version__


setup(packages=find_packages(include=['satella', 'satella.*']),
      version=__version__)
