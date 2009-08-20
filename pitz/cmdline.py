# vim: set expandtab ts=4 sw=4 filetype=python:


from __future__ import with_statement

import optparse, os, subprocess, warnings
warnings.simplefilter('ignore', DeprecationWarning)

from IPython.Shell import IPShellEmbed

from clepy import send_through_pager, spinning_distraction

from pitz import *
from pitz.project import Project


def pitz_shell():

    import logging, optparse, os, sys

    log = logging.getLogger('pitz')
    log.setLevel(logging.DEBUG)

    p = optparse.OptionParser()

    p.set_usage('%prog [path to project file]')

    options, args = p.parse_args()

    shell(*args)


def shell(picklefile=None, yamlfile=None):

    """
    Start an ipython session after loading in a project.
    """

    import logging, optparse, os, sys

    log = logging.getLogger('pitz.cmdline')
    log.setLevel(logging.DEBUG)

    p = optparse.OptionParser()

    p.add_option('-p', '--pitz-dir')

    options, args = p.parse_args()

    if picklefile:
        log.debug("Using picklefile")
        p = Project.from_pickle(picklefile)

    elif yamlfile:
        log.debug("Using yamlfile")
        p = Project.from_yaml_file(yamlfile)

    else:
        log.debug("Searching for yaml file...")
        p = Project.from_yaml_file(Project.find_yaml_file())

    # Everything in this dictionary will be added to the top-level
    # namespace in the shell.
    ns = dict([(C.__name__, C) for C in p.classes.values()])
    ns['p'] = p

    s = IPShellEmbed(['-colors', 'Linux'])
    s(local_ns=ns)

    # This stuff happens when you close the IPython session.
    answer = raw_input("Write out updated yaml files? ([y]/n) ")
    if answer.lower() not in ['n', 'no']:
        p.to_yaml_file()
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


def pitz_everything():

    with spinning_distraction():

        p = setup_options()

        options, args = p.parse_args()

        path_to_yaml_file = options.pitz_dir or Project.find_yaml_file()

        proj = Project.from_yaml_file(path_to_yaml_file)

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

        options, args = p.parse_args()

        path_to_yaml_file = options.pitz_dir or Project.find_yaml_file()

        proj = Project.from_yaml_file(path_to_yaml_file)

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


def pitz_add():

    from clepy import edit_with_editor
    from pitz.projecttypes.simplepitz import Task, Status, Estimate, \
    Milestone

    p = optparse.OptionParser()
    p.add_option('-p', '--pitz-dir')
    p.add_option('-t', '--title', help='Task title')
    p.set_usage('%prog [options] [filters]')

    options, args = p.parse_args()

    path_to_yaml_file = options.pitz_dir or Project.find_yaml_file()

    proj = Project.from_yaml_file(path_to_yaml_file)

    not_estimated = Estimate(proj, title='not estimated', points=None)

    t = Task(
        title=options.title or raw_input("Title: "),
        description=edit_with_editor(),
        status=Status(proj, title='unstarted'),
        milestone=proj.choose_value('milestone'),
        estimate=proj.choose_value('estimate', not_estimated),
    )

    proj.append(t)
    print("Added %s to the project." % t.summarized_view)
    proj.save_entities_to_yaml_files()


def pitz_show():

    import optparse, os, sys
    from pitz.project import Project
    from pitz.entity import Entity

    p = setup_options()

    options, args = p.parse_args()

    if not args:
        p.print_usage()
        sys.exit()

    path_to_yaml_file = options.pitz_dir or Project.find_yaml_file()

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

    import optparse, os, sys
    from pitz.project import Project

    p = optparse.OptionParser()
    p.add_option('-p', '--pitz-dir', help="Path to your pitzdir")
    p.set_usage('%prog [options] folder-to-store-html-files')

    options, args = p.parse_args()

    if not args or not os.path.isdir(args[0]):
        p.print_usage()
        sys.exit()

    path_to_yaml_file = options.pitz_dir or Project.find_yaml_file()

    proj = Project.from_yaml_file(path_to_yaml_file)

    htmldir = args[0]
    html_filename = os.path.join(htmldir, proj.html_filename)

    proj.to_html(html_filename)


    print("Wrote %d html files out of %d entities in project."
        % (
            len([e for e in proj if e.to_html_file(htmldir)]),
            len(proj)))

    # Record that we rebuilt all the HTML files.
    proj.save_entities_to_yaml_files()
