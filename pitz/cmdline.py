# vim: set expandtab ts=4 sw=4 filetype=python:

"""
These functions do the interesting stuff after options and arguments
have been parsed.
"""

import glob, os, sys

import yaml

from IPython.Shell import IPShellEmbed

import pitz

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
    if p:
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

    pitzfiles_dir = os.path.join(x, 'pitzfiles')

    os.mkdir(pitzfiles_dir)

    return pitzfiles_dir

# Create a project object and then save it out as a yaml file in the
# pitzfiles folder.

# Copy the selected project module over to the new directory.


# List all the possible project modules and wait for a choice.
def list_projects():
    
    print("__file__ is %s" % __file__)
