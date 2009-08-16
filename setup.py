from setuptools import setup, find_packages
import sys, os

from pitz import __version__
version = __version__

setup(
    name='pitz',
    version=version,
    description="Python to-do tracker inspired by ditz (ditz.rubyforge.org)",

    long_description="""\
ditz (http://ditz.rubyforge.org) is the best distributed ticketing
system that I know of.  There's a few things I want to change, so I
started pitz.""",

    classifiers=[],
    keywords='ditz',
    author='Matt Wilson',
    author_email='matt@tplus1.com',
    url='http://pitz.tplus1.com',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    package_dir={'pitz':'pitz'},

    zip_safe=False,

    install_requires=[
        'mock==0.4',
        'clepy',
        'IPython',
        'PyYAML',
        'sphinx',
        'nose',
        'jinja2',
          # -*- Extra requirements: -*-
    ],

    scripts = [
        'scripts/pitz-shell',
        'scripts/pitz-setup',
        'scripts/pitz-show',
        'scripts/pitz-html',
    ],

    entry_points="""
    [console_scripts]
    pitz-everything = pitz.cmdline:pitz_everything
    pitz-todo = pitz.cmdline:pitz_todo
    pitz-add = pitz.cmdline:pitz_add
    """,

    test_suite = 'nose.collector',

)
