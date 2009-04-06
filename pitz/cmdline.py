# vim: set expandtab ts=4 sw=4 filetype=python:

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

        P = getattr(m, projectdata['classname'])

        p = P.from_yaml_file(projectfile)

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
