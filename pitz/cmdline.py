# vim: set expandtab ts=4 sw=4 filetype=python:

from __future__ import with_statement

import logging, optparse, os, subprocess, sys, warnings
warnings.simplefilter('ignore', DeprecationWarning)

from IPython.Shell import IPShellEmbed

from clepy import edit_with_editor, send_through_pager, spinning_distraction

from pitz import *
from pitz.bag import Project

from pitz.entity import Comment, Component, Entity, Estimate, Milestone, \
Person, Status, Task

log = logging.getLogger('pitz.cmdline')


def print_version():

    from pitz import __version__
    print(__version__)
    sys.exit()


def pitz_shell():
    """
    Start an ipython session after loading in a project.
    """

    p = setup_options()

    options, args = p.parse_args()

    if options.version:
        print_version()

    pitzdir = Project.find_pitzdir(options.pitzdir)

    p = Project.from_pitzdir(pitzdir)
    p.find_me()

    # Everything in this dictionary will be added to the top-level
    # namespace in the shell.
    ns = dict([(C.__name__, C) for C in p.classes.values()])
    ns['p'] = p
    ns['send_through_pager'] = send_through_pager
    ns['edit_with_editor'] = edit_with_editor

    s = IPShellEmbed(['-colors', 'Linux'])
    s(local_ns=ns)

    # This stuff happens when you close the IPython session.
    answer = raw_input("Write out updated yaml files? ([y]/n) ").strip()
    if answer.lower() not in ['n', 'no']:
        p.to_yaml_file()
        p.to_pickle()
        p.save_entities_to_yaml_files()


def mk_pitzdir():

    """
    Creates a folder and returns the absolute path.
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

    return pitzdir


def list_projects(modulepaths=(
        'pitz.simplepitz', 
        'pitz.agilepitz')):

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

    p = optparse.OptionParser()

    p.add_option('--version', action='store_true',
        help='show pitz version')

    options, args = p.parse_args()

    if options.version:
        print_version()

    project_title = raw_input(
        "Project name?  (you can change it later)").strip()

    pitzdir = mk_pitzdir()

    proj = Project(pathname=pitzdir, title=project_title)

    # Save the project as a yaml file in the pitzfiles folder.
    pfile = proj.to_yaml_file()

    print("All done!  Run pitz-shell %s to start working..." % pfile)


def setup_options():
    p = optparse.OptionParser()

    p.add_option('-p', '--pitzdir')

    p.add_option('--version', action='store_true',
        help='show pitz version')

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


def pitz_everything():

    with spinning_distraction():

        p = setup_options()

        p.add_option('-g', '--grep',
            help='Filter to entities matching a regex')

        options, args = p.parse_args()

        if options.version:
            print_version()

        pitzdir = Project.find_pitzdir(options.pitzdir)

        proj = Project.from_pitzdir(pitzdir)
        proj.find_me()

        d = build_filter(args)

        results = proj

        if d:
            results = results(**d)

        if options.grep:
            results = results.grep(options.grep)

    send_through_pager(str(results))


def pitz_todo():

    with spinning_distraction():

        p = setup_options()

        p.add_option('-g', '--grep',
            help='Filter to entities matching a regex')

        options, args = p.parse_args()

        if options.version:
            print_version()

        pitzdir = Project.find_pitzdir(options.pitzdir)

        proj = Project.from_pitzdir(pitzdir)
        proj.find_me()

        d = build_filter(args)

        # This line here is the only thing different from
        # pitz_everything, so these two functions should be
        # consolidated.
        results = proj.todo

        # Apply filters.
        if d:
            results = results(**d)

        # Apply grep.
        if options.grep:
            results = results.grep(options.grep)

    send_through_pager(str(results))


def pitz_add_task():

    """
    Walks through the setup of a new Task.
    """


    p = setup_options()
    p.add_option('-t', '--title', help='Task title')

    options, args = p.parse_args()

    if options.version:
        print_version()

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    t = Task(

        proj,

        title=options.title or raw_input("Title: ").strip(),

        description=edit_with_editor('# Task description goes here'),

        status=Status(proj, title='unstarted'),

        milestone=Milestone.choose_from_already_instantiated(
            Milestone(proj, title='unscheduled')),

        estimate=Estimate.choose_from_already_instantiated(
            Estimate(proj, title='not estimated')),
    )

    proj.append(t)
    print("Added %s to the project." % t.summarized_view)
    proj.save_entities_to_yaml_files()

    return t


pitz_add = pitz_add_task


def pitz_show():


    p = setup_options()

    options, args = p.parse_args()

    if options.version:
        print_version()

    if not args:
        p.print_usage()
        sys.exit()

    path_to_yaml_file = options.pitzdir or Project.find_file()

    proj = Project.from_yaml_file(path_to_yaml_file)

    e = proj[args[0]]

    if isinstance(e, Entity):
        send_through_pager(e.detailed_view)

    else:
        print("Sorry, couldn't find %s" % args[1])


def pitz_html():

    """
    Write out a bunch of HTML files.
    """

    with spinning_distraction():

        p = setup_options()
        p.set_usage('%prog [options] directory')
        p.add_option('--force',
            help='Ignore timestamps and regenerate all files',
            action='store_true',
            default=False)

        options, args = p.parse_args()

        if options.version:
            print_version()

        if not args:
            p.print_usage()
            sys.exit()

        pitzdir = Project.find_pitzdir(options.pitzdir)

        proj = Project.from_pitzdir(pitzdir)
        proj.find_me()

        htmldir = args[0]

        proj.to_html(htmldir)

        print("Wrote %d html files out of %d entities in project."
            % (
                len([e for e in proj
                    if e.to_html_file(htmldir, options.force)]),
                len(proj)))

        # Record that we rebuilt all the HTML files.
        proj.save_entities_to_yaml_files()


def pitz_edit():

    p = setup_options()
    p.set_usage('%prog frag attribute-to-edit')

    options, args = p.parse_args()

    if options.version:
        print_version()

    if not args:
        p.print_usage()
        sys.exit()

    path_to_yaml_file = options.pitzdir or Project.find_file()

    proj = Project.from_yaml_file(path_to_yaml_file)

    e = proj[args[0]]
    e.edit(args[1])

    print("Edited %s on %s." % (args[1], args[0]))
    proj.save_entities_to_yaml_files()


def pitz_add_milestone():

    p = setup_options()
    p.add_option('-t', '--title', help='Milestone title')

    options, args = p.parse_args()

    if options.version:
        print_version()

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    m = Milestone(
        proj,
        title=options.title or raw_input("Title: ").strip(),
        description=edit_with_editor('# Milestone description goes here'),
        reached=Milestone.choose_from_allowed_values('reached', False),
    )

    proj.append(m)
    print("Added %s to the project." % m.summarized_view)
    proj.save_entities_to_yaml_files()


def pitz_add_person():

    p = setup_options()
    p.add_option('-t', '--title', help='Person title')

    options, args = p.parse_args()

    if options.version:
        print_version()

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    person = Person(
        proj,
        title=options.title or raw_input("Title: ").strip(),
        description=edit_with_editor('# Milestone description goes here'),
    )

    proj.append(person)
    print("Added %s to the project." % person.summarized_view)
    proj.save_entities_to_yaml_files()


def pitz_add_estimate():

    p = setup_options()
    p.add_option('-t', '--title', help='Estimate title')

    options, args = p.parse_args()

    if options.version:
        print_version()

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    est = Estimate(
        proj,
        title=options.title or raw_input("Title: ").strip(),
        description=edit_with_editor('# Estimate description goes here'),
        points=int(raw_input("Points: ").strip()),
    )

    proj.append(est)
    print("Added %s to the project." % est.summarized_view)
    proj.save_entities_to_yaml_files()


def pitz_add_component():

    p = setup_options()
    p.add_option('-t', '--title', help='Component title')

    options, args = p.parse_args()

    if options.version:
        print_version()

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    c = Component(
        proj,
        title=options.title or raw_input("Title: ").strip(),
        description=edit_with_editor('# Component description goes here'),
    )

    proj.append(c)
    print("Added %s to the project." % c.summarized_view)
    proj.save_entities_to_yaml_files()


def pitz_add_status():

    p = setup_options()
    p.add_option('-t', '--title', help='Status title')

    options, args = p.parse_args()

    if options.version:
        print_version()

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    s = Status(
        proj,
        title=options.title or raw_input("Title: ").strip(),
        description=edit_with_editor('# Status description goes here'),
    )

    proj.append(s)
    print("Added %s to the project." % s.summarized_view)
    proj.save_entities_to_yaml_files()
