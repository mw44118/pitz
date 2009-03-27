# vim: set expandtab ts=4 sw=4 filetype=python:

from IPython.Shell import IPShellEmbed
from pitz import *

def shell(pitzdir):

    p = Project('Pitz', pitzdir)

    s = IPShellEmbed(['-colors', 'Linux'])
    s()

    answer = raw_input("Write out updated yaml files? ([y]/n) ")
    if answer.lower() not in ['n', 'no']:
        p.to_yaml_files()

