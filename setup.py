from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='pitz',
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
    url='http://tplus1.com',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    package_dir={'pitz':'pitz'},

    zip_safe=False,

    install_requires=[
        'clepy',
        'IPython',
        'PyYAML',
        'sphinx',
        'nose',
        'jinja2',
          # -*- Extra requirements: -*-
    ],

    # I know about the much fancier entry points, but I prefer this
    # solution.  Why does everything have to be zany?
    scripts = [
        'scripts/pitz-shell',
        'scripts/pitz-setup',
        'scripts/pitz-todo',
        'scripts/pitz-show',
        'scripts/pitz-everything',
    ],

    test_suite = 'nose.collector',

)
