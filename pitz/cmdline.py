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


def pitz_shell():
    """
    Start an ipython session after loading in a project.
    """

    p = setup_options()

    options, args = p.parse_args()

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    p = Project.from_pitzdir(pitzdir)
    p._shell_mode = True
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
        return

    project_title = raw_input(
        "Project name?  (you can change it later) ").strip()

    pitzdir = mk_pitzdir()

    proj = Project(pathname=pitzdir, title=project_title)
    proj.to_yaml_file()

    pitz_me()

    for plural, add_function, singular in [
        ('estimates', pitz_add_estimate, 'estimate'),
        ('statuses', pitz_add_status, 'status'),
        ('milestones', pitz_add_milestone, 'milestone'),
        ('components', pitz_add_component, 'component')]:

        temp = raw_input("Add some %s to the project? (y/n)" % plural)

        while temp.strip().lower().startswith('y'):

            add_function()
            temp = raw_input("Add another %s? (y/n)" % singular)

    proj.save_entities_to_yaml_files()
    print("All done!")


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
            return

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
            return

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
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    t = Task(

        proj,

        title=options.title or raw_input("Task title: ").strip(),

        description=edit_with_editor('# Task description goes here'),

        status=Status(proj, title='unstarted'),

        milestone=Milestone.choose_from_already_instantiated(
            Milestone(proj, title='unscheduled')),

        estimate=Estimate.choose_from_already_instantiated(
            Estimate(proj, title='not estimated')),

        owner=Person.choose_from_already_instantiated(),
    )

    proj.append(t)

    temp = raw_input("Add some components for this task? (y/n)")

    if temp and temp.strip().lower().startswith('y'):
        t['components'] = Component.choose_many_from_already_instantiated()


    print("Added %s to the project." % t.summarized_view)
    proj.save_entities_to_yaml_files()

    return t


pitz_add = pitz_add_task


def pitz_show():


    p = setup_options()

    options, args = p.parse_args()

    if options.version:
        print_version()
        return

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
            return

        if not args:
            p.print_usage()
            sys.exit()

        pitzdir = Project.find_pitzdir(options.pitzdir)

        proj = Project.from_pitzdir(pitzdir)
        proj.find_me()

        htmldir = args[0]

        proj.to_html(htmldir)

        proj.todo.to_html(htmldir)
        proj.milestones.to_html(htmldir)
        proj.tasks.to_html(htmldir)
        proj.components.to_html(htmldir)

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
        return

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
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    m = Milestone(
        proj,
        title=options.title or raw_input("Milestone title: ").strip(),
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
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    person = Person(
        proj,
        title=options.title or raw_input("Person title: ").strip(),
        description=edit_with_editor('# Person description goes here'),
    )

    proj.append(person)
    print("Added %s to the project." % person.summarized_view)
    proj.save_entities_to_yaml_files()

    if raw_input("Should I identify you as %(title)s? (y/N)" % person)\
    .strip().lower().startswith('y'):

        person.save_as_me_yaml()
        print("OK, I'll recognize you as %(title)s from now on.")


def pitz_add_estimate():

    p = setup_options()
    p.add_option('-t', '--title', help='Estimate title')

    options, args = p.parse_args()

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    est = Estimate(
        proj,
        title=options.title or raw_input("Estimate title: ").strip(),
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
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    c = Component(
        proj,
        title=options.title or raw_input("Component title: ").strip(),
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
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    s = Status(
        proj,
        title=options.title or raw_input("Status title: ").strip(),
        description=edit_with_editor('# Status description goes here'),
    )

    proj.append(s)
    print("Added %s to the project." % s.summarized_view)
    proj.save_entities_to_yaml_files()


def pitz_destroy():

    p = setup_options()
    p.add_option('-t', '--title', help='Status title')

    options, args = p.parse_args()

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    e = proj[args[0]]

    if isinstance(e, Entity):

        e.self_destruct(proj)

    print("""%(frag)s: "%(title)s" is no longer part of the project."""
        % e)

    proj.save_entities_to_yaml_files()


def pitz_my_tasks():

    p = setup_options()

    options, args = p.parse_args()

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    if not proj.me:
        print("Sorry, I don't know who you are.")
        print("Use pitz-me to add yourself to the project.")
        sys.exit()

    my_tasks = proj.todo(owner=proj.me)
    my_tasks.title = "To-do list for %(title)s" % proj.me

    if my_tasks:
        send_through_pager(str(my_tasks))

    else:
        print("I didn't find any tasks for you (%(title)s)."
            % proj.me)


def pitz_me():

    """
    Pick a Person or make a new one, then save a me.yaml file.
    """

    p = setup_options()

    options, args = p.parse_args()

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    if proj.me:
        print("You are %(title)s." % proj.me)
        print("Delete this file if you want to be somebody else:")
        print(os.path.join(proj.pathname, 'me.yaml'))
        return

    if Person.already_instantiated:
        print("You may already be in pitz:")
        person = Person.choose_from_already_instantiated()
        person.save_as_me_yaml()

        print("OK, I'll recognize you as %(title)s from now on."
            % person)

        return

    pitz_add_person()


def pitz_claim_task():
    
    p = setup_options()
    p.set_usage("%prog task")

    options, args = p.parse_args()

    if not args:
        p.print_usage()
        return

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    if not proj.me:
        print("Sorry, I don't know who you are.")
        print("Use pitz-me to add yourself to the project.")
        return

    t = proj[args[0]]
    t.assign(proj.me)
    proj.save_entities_to_yaml_files()


def pitz_assign_task():

    p = setup_options()
    p.set_usage("%prog task [person]")

    options, args = p.parse_args()

    if not args:
        p.print_usage()
        return

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    t = proj[args[0]]

    if len(args) == 2:
        person  = proj[args[1]]

    else:
        person = Person.choose_from_already_instantiated()

        if not person:
            print("Pick somebody!")
            return

    t.assign(person)
    proj.save_entities_to_yaml_files()


def pitz_finish_task():

    p = setup_options()
    p.set_usage("%prog task")

    options, args = p.parse_args()

    if not args:
        p.print_usage()
        return

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    t = proj[args[0]]
    t.finish()
    proj.save_entities_to_yaml_files()


def pitz_start_task():

    """
    Set the task's status to started and set the owner to you.
    """

    p = setup_options()
    p.set_usage("%prog task")

    options, args = p.parse_args()

    if not args:
        p.print_usage()
        return

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    if not proj.me:
        print("Sorry, I don't know who you are.")
        print("Use pitz-me to add yourself to the project.")
        sys.exit()

    t = proj[args[0]]
    t.assign(proj.me)
    t.start()
    proj.save_entities_to_yaml_files()


def pitz_abandon_task():

    p = setup_options()
    p.set_usage("%prog task")

    options, args = p.parse_args()

    if not args:
        p.print_usage()
        return

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    t = proj[args[0]]
    t.abandon()
    proj.save_entities_to_yaml_files()
