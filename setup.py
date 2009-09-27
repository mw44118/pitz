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
        'Tempita',
          # -*- Extra requirements: -*-
    ],


    entry_points="""
    [console_scripts]
    pitz-everything = pitz.cmdline:pitz_everything
    pitz-todo = pitz.cmdline:pitz_todo
    pitz-add = pitz.cmdline:pitz_add
    pitz-shell = pitz.cmdline:pitz_shell
    pitz-setup = pitz.cmdline:pitz_setup
    pitz-show = pitz.cmdline:pitz_show
    pitz-html = pitz.cmdline:pitz_html
    pitz-edit = pitz.cmdline:pitz_edit
    pitz-add-task = pitz.cmdline:pitz_add_task
    pitz-add-milestone = pitz.cmdline:pitz_add_milestone
    pitz-add-person = pitz.cmdline:pitz_add_person
    pitz-add-status = pitz.cmdline:pitz_add_status
    pitz-add-estimate = pitz.cmdline:pitz_add_estimate
    pitz-add-component = pitz.cmdline:pitz_add_component
    pitz-destroy = pitz.cmdline:pitz_destroy
    """,

    test_suite = 'nose.collector',

)
