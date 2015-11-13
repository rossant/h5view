from setuptools import setup
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.md')).read()
except IOError:
    README = ''

setup(name='h5view',
      long_description=README,
      license='LICENSE.md',
      py_modules=['h5view'],
      )
