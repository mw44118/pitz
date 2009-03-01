from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pitz',
      version=version,
      description="Python implementation of ditz (ditz.rubyforge.org)",

      long_description="""\
ditz (http://ditz.rubyforge.org) is the best distributed ticketing
system that I know of.  It uses yaml to store all the information about
the status of projects, so I'm going to try to write a python
interface.""",

      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ditz',
      author='Matt Wilson',
      author_email='matt@tplus1.com',
      url='http://tplus1.com',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'PyYAML',
        'sphinx',
        'nose',
        'jinja2',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,

      test_suite = 'nose.collector',

      )
