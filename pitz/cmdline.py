# vim: set expandtab ts=4 sw=4 filetype=python:

from IPython.Shell import IPShellEmbed
from pitz import *

def main():

    p = Project('Pitz', 
        '/home/matt/projects/pitz/pitz/.pitz')

    tampered = False
    p.tampered = False
    s = IPShellEmbed(['-colors', 'Linux'])
    s()

    print("p.tampered is %s" % p.tampered)
    print("tampered is %s" % tampered)

