# vim: set expandtab ts=4 sw=4 filetype=python:

"""
These functions do the interesting stuff after options and arguments
have been parsed.
"""

import optparse, os, subprocess

import IPython.ipapi

from pitz import *
from pitz.project import Project
from pitz.entity import ImmutableEntity

def shell(projectfile=None):

    """
    Start an ipython session after loading in a project.
    """

    if projectfile:
        p = Project.from_yaml_file(projectfile)

    else:
        p = Project.from_yaml_file(Project.find_yaml_file())

    # Everything in this dictionary will be added to the top-level
    # namespace in the shell.
    ns = dict([(C.__name__, C) for C in p.classes.values()])
    ns['p'] = p

    IPython.ipapi.launch_new_instance(ns)

    # This stuff happens when you close the IPython session.
    answer = raw_input("Write out updated yaml files? ([y]/n) ")
    if answer.lower() not in ['n', 'no']:
        p.to_yaml_file()
        p.save_entities_to_yaml_files()


def mk_pitzdir():
    """
    Returns the path to the newly created folder.
    """

    msg = """\
I need to make a directory named 'pitzdir'.  Where should I put it?
The default place is right here (.)."""

    x = raw_input(msg)

    if not x:
        x = '.'

    if not os.access(x, os.W_OK):
        raise ValueError("I can't write to path %s!" % x)

    pitzdir = os.path.abspath(os.path.join(x, 'pitzdir'))

    os.mkdir(pitzdir)

    if not os.path.isdir(pitzdir):
        raise Exception("Arrgh!")

    return pitzdir


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

    project_title = raw_input("Project name?  (you can change it later)")

    pitzdir = mk_pitzdir()

    # List all the possible project modules and wait for a choice.
    m = list_projects()

    # Create a project instance based on the chosen module.
    ProjectClass = getattr(m, m.myclassname)
    p = ProjectClass(pathname=pitzdir, title=project_title)

    # Save the project as a yaml file in the pitzfiles folder.
    pfile = p.to_yaml_file()

    print("All done!  Run pitz-shell %s to start working..." % pfile)


def setup_options():
    p = optparse.OptionParser()

    p.add_option('-p', '--pitz-dir')
    p.add_option('-g', '--grep')

    p.set_usage('%prog [options] [filters]')

    return p

def build_filter(args):
    """
    Return a dictionary suitable for filtering.

    >>> build_filter(['a=1', 'b=2', 'c=[3,4,5]'])
    {'a': '1', 'c': ['3', '4', '5'], 'b': '2'}

    """

    d = dict()
    for a in args:
        attr, value = a.split('=')

        # Make a list of values if we got a string like "[1, 2, 3]"
        if value.startswith('[') and value.endswith(']'):
            value = value.strip('[]').split(',')

        d[attr] = value

    return d


def send_through_pager(s):
    """
    Open up this user's pager and send string s through it.

    If I don't find a $PAGER variable and "which less" fails, I'll just
    print the string.
    """

    pager = os.environ.get('PAGER')

    if not pager:
        return_code = subprocess.call(['which', 'less'])

        # The which program returns zero when it found stuff.
        if return_code == 0:
            pager = 'less'

    if pager:
        p = subprocess.Popen([pager], stdin=subprocess.PIPE)
        p.communicate(s)

    else:
        print(s)
