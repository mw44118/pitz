# vim: set expandtab ts=4 sw=4 filetype=python:

from IPython.Shell import IPShellEmbed
from pitz import *

def shell(projectfile):

    p = Project.from_yaml_file(projectfile)

    s = IPShellEmbed(['-colors', 'Linux'])
    s()


    # This stuff happens when you close the IPython session.
    answer = raw_input("Write out updated yaml files? ([y]/n) ")
    if answer.lower() not in ['n', 'no']:
        p.to_yaml_file()
        p.save_entities_to_yaml_files()
