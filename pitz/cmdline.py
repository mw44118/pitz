# vim: set expandtab ts=4 sw=4 filetype=python:

"""
These functions do the interesting stuff after options and arguments
have been parsed.
"""

import glob, os, sys

import yaml

from IPython.Shell import IPShellEmbed

import pitz
from pitz import *

def shell(projectfile=None):

    """
    Start an ipython session and possibly load in a project.
    """

    if projectfile:
        projectdata = yaml.load(open(projectfile))

        # Read the section on __import__ at
        # http://docs.python.org/library/functions.html
        # to make sense out of this.
        m = __import__(projectdata['module'],
            fromlist=projectdata['classname'])

        # This big P is the class of the project.
        P = getattr(m, projectdata['classname'])

        # This little p is an instance of the class.
        p = P.from_yaml_file(projectfile)

        # Normally, I hate stuff like this, but I want to put all the
        # classes for this project into the namespace, and I can't
        # predict the names for the classes.
        locals().update([(C.__name__, C) for C in P.classes.values()])

    else:
        p = None

    s = IPShellEmbed(['-colors', 'Linux'])
    s()

    # This stuff happens when you close the IPython session.
    if p is not None:
        answer = raw_input("Write out updated yaml files? ([y]/n) ")
        if answer.lower() not in ['n', 'no']:
            p.to_yaml_file()
            p.save_entities_to_yaml_files()


def mk_pitzfiles_folder():
    """
    Returns the path to the newly created folder.
    """

    msg = """\
I need to make a directory named 'pitzfiles'.  Where should I put it?
The default place is right here (.)."""

    x = raw_input(msg)

    if not x:
        x = '.'

    if not os.access(x, os.W_OK):
        raise ValueError("I can't write to path %s!" % x)

    pitzfiles_dir = os.path.abspath(os.path.join(x, 'pitzfiles'))

    os.mkdir(pitzfiles_dir)

    if not os.path.isdir(pitzfiles_dir):
        raise Exception("Arrgh!")

    return pitzfiles_dir


def list_projects(modulepaths=(
        'pitz.projecttypes.simplepitz', 
        'pitz.projecttypes.agilepitz')):

    """
    Print a list of modules to choose from and return the chosen one.
    """

    modules = [namedModule(mp) for mp in modulepaths]
    for i, m in enumerate(modules):
        print("%4d. %s: %s" % (i, m.__name__, m.__doc__))

    return modules[int(raw_input("Choose one."))]
        

def namedModule(name):
    """
    Return a module given its name.

    Copied from
    http://twistedmatrix.com/trac/browser/trunk/twisted/python/reflect.py

    Thanks to "dash" in #python for the recommendation.
    """

    topLevel = __import__(name)
    packages = name.split(".")[1:]
    m = topLevel
    for p in packages:
        m = getattr(m, p)
    return m


def pitz_setup():

    pathname = mk_pitzfiles_folder()

    # List all the possible project modules and wait for a choice.
    m = list_projects()

    # Create a project object based on the chosen module.
    p = getattr(m, m.myclassname)(pathname=pathname)

    # Save the project as a yaml file in the pitzfiles folder.
    pfile = p.to_yaml_file()

    print("All done!  Run pitz-shell %s to start working..." % pfile)
