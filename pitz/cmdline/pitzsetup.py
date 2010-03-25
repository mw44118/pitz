# vim: set expandtab ts=4 sw=4 filetype=python:

import optparse
import os
import pwd
import textwrap

from pitz.project import Project
from pitz.entity import Person, Status
from pitz.cmdline import print_version


def mk_pitzdir():
    """
    Creates the pitzdir folder, the hooks folder inside that, and copies
    in all the example hook files.

    Returns the absolute path.
    """

    x = os.getcwd()

    if not os.access(x, os.W_OK):
        raise ValueError("I can't write to path %s!" % x)

    pitzdir = os.path.abspath(os.path.join(x, 'pitzdir'))
    hooksdir = os.path.join(pitzdir, 'hooks')

    os.mkdir(pitzdir)
    os.mkdir(hooksdir)

    # TODO: Consider how to just copy a file in, rather than writing a
    # file from here.  It gets a little tricky since I might be running
    # this script from within an egg, so I might not be able to know
    # where the .example files live.

    # Once I have numerous example scripts I want to copy, this is going
    # to get silly.  But for now, it will work OK.

    f = open(
        os.path.join(
            hooksdir, 'after_saving_entities_to_yaml_files.example'),
        'w')

    f.write(textwrap.dedent("""\
        #! /bin/bash

        # Make this file executable to enable it.
        echo "Starting the after_saving_entities_to_yaml_files hook..."
        git add $1/.
        echo "Finished the after_saving_entities_to_yaml_files hook."
        """))

    return pitzdir


def pitz_setup():

    """
    Start a new project
    """

    p = optparse.OptionParser()

    p.epilog = "Set up pitz"

    p.add_option('--version', action='store_true',
        help='show pitz version')

    options, args = p.parse_args()

    if options.version:
        print_version()
        return

    dir = os.path.basename(os.getcwd())

    project_name = raw_input(
        "Project name (hit ENTER for %s): " % dir).strip()

    if not project_name:
        project_name = dir

    pitzdir = mk_pitzdir()

    proj = Project(pathname=pitzdir, title=project_name)
    proj.to_yaml_file()

    Status.setup_defaults(proj)

    pw_name = pwd.getpwuid(os.getuid()).pw_name

    name = raw_input("Your name (hit ENTER for %s): " % pw_name).strip()

    if not name:
        name = pw_name

    person = Person(proj, title=name)

    proj.save_entities_to_yaml_files()
    print("All done!")
    print("Run pitz-add-task to add a task, or run pitz-help for help.")

pitz_setup.script_name = 'pitz-setup'
