# vim: set expandtab ts=4 sw=4 filetype=python:

from __future__ import with_statement

import logging, optparse, os, pwd, sys, warnings

warnings.simplefilter('ignore', DeprecationWarning)

from wsgiref.simple_server import make_server

from IPython.Shell import IPShellEmbed

import clepy

from pitz import *
from pitz.project import Project

from pitz.entity import Component, Entity, Estimate, Milestone, \
Person, Status, Task

from pitz.webapp import SimpleWSGIApp

log = logging.getLogger('pitz.cmdline')

class PitzHelp(object):

    def add_to_list_of_scripts(self, f):

        if not hasattr(self, 'scripts'):
            self.scripts = {}

        self.scripts[f.script_name] = f.__doc__.strip() \
        if f.__doc__ else 'No description'

        return f


    def __call__(self):

        for name, description in sorted(self.scripts.items()):
            print("    %-26s %-44s" % (name, clepy.maybe_add_ellipses(description, 44)))

pitz_help = PitzHelp()
f = pitz_help.add_to_list_of_scripts


class PitzScript(object):

    """
    Got this idea from a commenter, Linus, on my blog here:

    http://blog.tplus1.com/index.php/2009/10/18/help-me-rewrite-some-repetitive-scripts/

    Thanks Linus!

    This is the generic script class.
    """

    def __init__(self, title=None, save_proj=True, script_name=None,
        doc=None, **filter):

        self.save_proj = save_proj
        self.filter = filter
        self.title = title

        if script_name:
            self.script_name = script_name

        if doc:
            self.__doc__ = doc

    def handle_p(self, p):
        """
        Use this to monkey with the optparse.OptionParser instance p.
        For example, set a specific usage message, or add an extra
        option.
        """


    def handle_options_and_args(self, p, options, args):
        """
        Use this to examine the options and args parsed from the
        command line.  Usually, at this point, scripts will make sure
        they got all the right args and options.
        """


    def handle_proj(self, p, options, args, proj, results):
        """
        Do the interesting stuff of the script in here.
        """

    def apply_filter_and_grep(self, p, options, args, b):

        """
        Return a new bag after filtering and using grep on the bag b
        passed in.
        """

        filter = build_filter(args)

        results = b

        if filter:
            results = results(**filter)

        if options.grep:
            results = results.grep(options.grep)

        return results


    def setup_p(self):
        p = optparse.OptionParser()

        p.add_option('-p', '--pitzdir')

        p.add_option('--version', action='store_true',
            help='show pitz version')

        return p


    def setup_options_and_args(self, p):

        options, args = p.parse_args()

        if options.version:
            from pitz import __version__
            print(__version__)
            raise SystemExit

        return options, args


    def setup_proj(self, p, options, args):

        pitzdir = Project.find_pitzdir(options.pitzdir)
        pidfile = write_pidfile_or_die(pitzdir)
        proj = Project.from_pitzdir(pitzdir)
        proj.pidfile = pidfile
        proj.find_me()

        return proj


    def setup_results(self, p, options, args, proj):

        if self.filter:
            results = proj(**self.filter)

        else:
            results = proj

        return results


    def add_grep_option(self, p):

        p.add_option('-g', '--grep',
            help='Filter to entities matching a regex')

        return p


    def add_view_options(self, p):

        p.add_option('--one-line-view', help='single line view',
            dest='custom_view', action='store_const', const='one_line_view')

        p.add_option('--summarized-view', help='summarized view (default)',
            dest='custom_view', action='store_const', const='summarized_view')

        p.add_option('--detailed-view', help='detailed view',
            dest='custom_view', action='store_const', const='detailed_view')

        p.add_option('--abbr-view', help='abbreviated view',
            dest='custom_view', action='store_const', const='abbr')

        p.add_option('--frag-view', help='fragment view',
            dest='custom_view', action='store_const', const='frag')

        return p


    def __call__(self):

        with clepy.spinning_distraction():

            p = self.setup_p()

            # Call to the first specialized function.
            self.handle_p(p)

            options, args = self.setup_options_and_args(p)

            # Call the second specialized function.
            self.handle_options_and_args(p, options, args)

            proj = self.setup_proj(p, options, args)
            results = self.setup_results(p, options, args, proj)

        # Third special function.
        self.handle_proj(p, options, args, proj, results)

        if self.save_proj:
            proj.save_entities_to_yaml_files()

        os.remove(proj.pidfile)


class MyTasks(PitzScript):

    """
    List my tasks
    """

    script_name = 'pitz-my-tasks'

    def handle_p(self, p):
        self.add_grep_option(p)
        self.add_view_options(p)

    def handle_proj(self, p, options, args, proj, results):

        if not proj.me:
            print("Sorry, I don't know who you are.")
            print("Use pitz-me to add yourself to the project.")
            raise SystemExit

        if proj.me.my_tasks:

            results = self.apply_filter_and_grep(
                p, options, args, proj.me.my_tasks)

            clepy.send_through_pager(results.custom_view(
                options.custom_view or 'summarized_view'),
                clepy.figure_out_pager())

        else:
            print("I didn't find any tasks for you (%(title)s)."
                % proj.me)


class PitzEverything(PitzScript):

    """
    Everything in the project
    """

    script_name = 'pitz-everything'

    def handle_p(self, p):
        self.add_grep_option(p)
        self.add_view_options(p)


    def handle_proj(self, p, options, args, proj, results):

        results = self.apply_filter_and_grep(p, options, args, results)

        if self.title:
            results.title = "%s: %s" % (proj.title, self.title)

        clepy.send_through_pager(results.custom_view(
            options.custom_view or 'summarized_view'),
            clepy.figure_out_pager())


class PitzTodo(PitzScript):

    """
    List every unstarted and started task in the project.
    """

    script_name = 'pitz-todo'


    def handle_p(self, p):
        self.add_grep_option(p)
        self.add_view_options(p)


    def handle_proj(self, p, options, args, proj, results):

        results = self.apply_filter_and_grep(p, options, args, proj.todo)
        results.title = proj.todo.title

        clepy.send_through_pager(results.custom_view(
            options.custom_view or 'summarized_view'),
            clepy.figure_out_pager())


class RecentActivity(PitzScript):

    def handle_p(self, p):
        self.add_grep_option(p)
        self.add_view_options(p)

    def handle_proj(self, p, options, args, proj, results):

        results = self.apply_filter_and_grep(
            p, options, args, proj.recent_activity)

        clepy.send_through_pager(results.custom_view(
            options.custom_view or 'summarized_view'),
            clepy.figure_out_pager())


def print_version():

    from pitz import __version__
    print(__version__)


def pid_is_running(pid):

    """
    Return pid if pid is still going.

    >>> import os
    >>> mypid = os.getpid()
    >>> mypid == pid_is_running(mypid)
    True
    >>> pid_is_running(1000000) == None
    True
    """

    try:
        os.kill(pid, 0)

    except OSError:
        return

    else:
        return pid


def write_pidfile_or_die(pitzdir):

    pidfile = os.path.join(pitzdir, 'pitz.pid')

    if os.path.exists(pidfile):

        pid = int(open(pidfile).read())

        if pid_is_running(pid):

            print("Sorry, found a pidfile!  Kill process %s." % pid)

            raise SystemExit

        else:

            os.remove(pidfile)

    open(pidfile, 'w').write(str(os.getpid()))
    return pidfile


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

    pidfile = write_pidfile_or_die(pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj._shell_mode = True
    proj.find_me()

    # Everything in this dictionary will be added to the top-level
    # namespace in the shell.
    ns = dict([(C.__name__, C) for C in proj.classes.values()])
    ns['p'] = proj
    ns['send_through_pager'] = clepy.send_through_pager
    ns['edit_with_editor'] = clepy.edit_with_editor

    s = IPShellEmbed(['-colors', 'Linux'])
    s(local_ns=ns)

    # This stuff happens when you close the IPython session.
    answer = raw_input("Write out updated yaml files? ([y]/n) ").strip()
    if answer.lower() not in ['n', 'no']:
        proj.to_yaml_file()
        proj.to_pickle()
        proj.save_entities_to_yaml_files()

    # Remove the pidfile.
    os.remove(pidfile)

pitz_shell.script_name = 'pitz-shell'
f(pitz_shell)


def mk_pitzdir():

    """
    Creates a folder and returns the absolute path.
    """

    x = os.getcwd()

    if not os.access(x, os.W_OK):
        raise ValueError("I can't write to path %s!" % x)

    pitzdir = os.path.abspath(os.path.join(x, 'pitzdir'))

    os.mkdir(pitzdir)

    return pitzdir


def pitz_setup():

    """
    Start a new project
    """

    p = optparse.OptionParser()

    p.add_option('--version', action='store_true',
        help='show pitz version')

    options, args = p.parse_args()

    if options.version:
        print_version()
        return

    dir = os.path.basename(os.getcwd())

    project_title = raw_input(
        "Project name (hit ENTER for %s): " % dir).strip()

    if not project_title:
        project_title = dir

    pitzdir = mk_pitzdir()

    proj = Project(pathname=pitzdir, title=project_title)
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
f(pitz_setup)

def setup_options():
    p = optparse.OptionParser()

    p.add_option('-p', '--pitzdir')

    p.add_option('--version', action='store_true',
        help='show pitz version')

    return p


class PitzShow(PitzScript):

    """
    Show detailed view of one entity
    """

    script_name = 'pitz-show'

    def handle_p(self, p):
        p.set_usage("%prog frag")

    def handle_options_and_args(self, p, options, args):
        if not args:
            p.print_usage()
            raise SystemExit

    def handle_proj(self, p, options, args, proj, results):

        e = proj[args[0]]

        if isinstance(e, Entity):

            clepy.send_through_pager(
                e.detailed_view,
                clepy.figure_out_pager())

        else:
            print("Sorry, couldn't find %s" % args[1])


def pitz_html():

    """
    Write out a bunch of HTML files.
    """

    with clepy.spinning_distraction():

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

    pitzdir = Project.find_pitzdir(options.pitzdir)

    pidfile = write_pidfile_or_die(pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    e = proj[args[0]]
    e.edit(args[1])

    print("Edited %s on %s." % (args[1], args[0]))
    proj.save_entities_to_yaml_files()

    os.remove(pidfile)


def pitz_add_milestone():

    p = setup_options()
    p.add_option('-t', '--title', help='Milestone title')

    options, args = p.parse_args()

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    pidfile = write_pidfile_or_die(pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    m = Milestone(
        proj,
        title=options.title or raw_input("Milestone title: ").strip(),
        description=clepy.edit_with_editor('# Milestone description goes here'),
        reached=Milestone.choose_from_allowed_values('reached', False),
    )

    proj.append(m)
    print("Added %s to the project." % m.summarized_view)
    proj.save_entities_to_yaml_files()

    os.remove(pidfile)


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
        description=clepy.edit_with_editor('# Person description goes here'),
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

    p.add_option('--from-builtin-estimates',
        action='store_true',
        help='Choose from estimates I already made')

    options, args = p.parse_args()

    if options.version:
        print_version()
        raise SystemExit

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    if options.from_builtin_estimates:

        print("Right now, you got %d estimates in your project."
            % (proj.estimates.length))

        range = Estimate.choose_estimate_range()
        if range:
            print("Adding...")
            Estimate.add_range_of_estimates_to_project(proj, range)
            proj.save_entities_to_yaml_files()

        raise SystemExit

    est = Estimate(
        proj,
        title=options.title or raw_input("Estimate title: ").strip(),
        description=clepy.edit_with_editor('# Estimate description goes here'),
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
        description=clepy.edit_with_editor('# Component description goes here'),
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
        description=clepy.edit_with_editor('# Status description goes here'),
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
        choice = Person.choose_from_already_instantiated()
        if choice:
            person = choice
            person.save_as_me_yaml()

            print("OK, I'll recognize you as %(title)s from now on."
                % person)

            return

    print("I'll add you to pitz.")
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

    """
    Add this task to somebody's to-do list
    """

    script_name = 'pitz-assign-task'

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


class PitzStartTask(PitzScript):

    """
    Begin a task
    """

    script_name = 'pitz-start-task'

    def handle_p(self, p):
        p.set_usage("%prog task")

        p.add_option('-m', '--message',
            help="Store a comment")

    def handle_options_and_args(self, p, options, args):

        if not args:
            p.print_usage()
            raise SystemExit

    def handle_proj(self, p, options, args, proj, results):

        if not proj.me:
            print("Sorry, I don't know who you are.")
            print("Use pitz-me to add yourself to the project.")
            sys.exit()

        t = proj[args[0]]
        t.assign(proj.me)

        try:
            t.start(options.message)
        except ValueError, ex:
            print(ex.message)


class RefreshPickle(PitzScript):

    """
    Rebuild the pickle file from the yaml files.
    """

    script_name = 'pitz-refresh-pickle'

    def hande_project(self, p, options, args, proj, results):
        proj.to_pickle()



class PitzFinishTask(PitzStartTask):

    """
    Finish a task
    """

    script_name = 'pitz-finish-task'

    def handle_proj(self, p, options, args, proj, results):

        if not proj.me:
            print("Sorry, I don't know who you are.")
            print("Use pitz-me to add yourself to the project.")
            sys.exit()

        t = proj[args[0]]
        t.assign(proj.me)
        t.finish(options.message)



class PitzAbandonTask(PitzStartTask):

    """
    Abandon a task
    """

    script_name = 'pitz-abandon-task'

    def handle_proj(self, p, options, args, proj, results):
        proj[args[0]].abandon(options.message)


class PitzUnassignTask(PitzStartTask):

    """
    Take this task off somebody's list of stuff to do.
    """

    script_name = 'pitz-unassign-task'

    def handle_proj(self, p, options, args, proj, results):
        t = proj[args[0]]
        if 'owner' in t:
            t.pop('owner')

            # This is just to force the yaml file to be rewritten out.
            t['title'] = t['title']


class PitzPrioritizeAbove(PitzScript):

    """
    Put one task in front of another task
    """

    script_name = 'pitz-prioritize-above'

    def handle_p(self, p):
        p.set_usage("%prog frag1 frag2")

        p.add_option('-m', '--message',
            help="Store a comment")

    def handle_proj(self, p, options, args, proj, results):
        t1 = proj[args[0]]
        t2 = proj[args[1]]
        t1.prioritize_above(t2)

        if options.message:
            t1.comment(title=options.message, description='')


class PitzPrioritizeBelow(PitzPrioritizeAbove):

    """
    Put one task behind another task
    """

    script_name = 'pitz-prioritize-below'

    def handle_proj(self, p, options, args, proj, results):
        t1 = proj[args[0]]
        t2 = proj[args[1]]
        t1.prioritize_below(t2)

        if options.message:
            t1.comment(title=options.message, description='')


class PitzAddTask(PitzScript):

    script_name = 'pitz-add-task'

    def handle_p(self, p):
        p.add_option('-t', '--title', help='Task title')

        p.add_option('--no-description',
            action='store_true',
            help='Stores this task with an empty description')

        p.add_option('--use-defaults',
            action='store_true',
            help="Don't prompt for milestone, estimate, owner, or components")

    def handle_proj(self, p, options, args, proj, results):

        default_milestone = Milestone(proj, title='unscheduled')
        default_estimate = Estimate(proj, title='not estimated')
        default_owner = Person(proj, title='no owner')
        default_components = list()

        t = Task(

            proj,

            title=options.title or raw_input("Task title: ").strip(),

            description='' if options.no_description else clepy.edit_with_editor(
                '# Task description goes here'),

            status=Status(proj, title='unstarted'),

            milestone=default_milestone if options.use_defaults \
            else Milestone.choose_from_already_instantiated(default_milestone),

            estimate=default_estimate if options.use_defaults \
            else Estimate.choose_from_already_instantiated(default_estimate),

            owner=default_owner if options.use_defaults \
            else Person.choose_from_already_instantiated(default_owner),

            components=default_components if options.use_defaults \
            else Component.choose_many_from_already_instantiated(),

        )

        proj.append(t)

        print("Added %r to the project." % t)


def pitz_webapp():

    """
    Returns files asked for.

    Later on, will be awesome.
    """

    p = setup_options()

    options, args = p.parse_args()

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    httpd = make_server('', 8000, SimpleWSGIApp(proj))
    print "Serving on port 8000..."
    httpd.serve_forever()


def pitz_estimate_task():

    # Start of code to set up project.
    p = setup_options()
    p.set_usage("%prog task [estimate]")

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

    # end of code to set up project.

    t = proj[args[0]]

    if len(args) == 2:
        est = proj[args[1]]

    else:
        est = Estimate.choose_from_already_instantiated()

    t['estimate'] = est

    # Save the project.
    proj.save_entities_to_yaml_files()


def pitz_attach_file():

    # Generic.
    p = setup_options()

    # Every script may have a slightly different usage.
    p.set_usage("%prog entity file-to-attach")

    # This is generic.
    options, args = p.parse_args()

    if options.version:
        print_version()
        return
    # End of generic stuff.

    # Every script may have different required args.
    if len(args) != 2:
        p.print_usage()
        return

    # Generic code to build the project.
    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    # Start of interesting stuff that is specific just for this script.
    e, filepath = proj[args[0]], args[1]

    e.save_attachment(filepath)

    # Save the project. (This could also be generic).
    proj.save_entities_to_yaml_files()


def pitz_frags():
    """
    Prints all the frags in this project.

    I wrote this for command-line tab completion on fragments.
    """

    p = setup_options()
    p.set_usage("%prog")
    options, args = p.parse_args()

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    print('\n'.join([
        x.split('-')[1][:6]
        for x in os.listdir(pitzdir)
        if '-' in x]))


# These scripts change stuff.
pitz_start_task = pitz_help.add_to_list_of_scripts(PitzStartTask())
pitz_finish_task = f(PitzFinishTask())
pitz_abandon_task = f(PitzAbandonTask())
pitz_unassign_task = f(PitzUnassignTask())
pitz_prioritize_above = f(PitzPrioritizeAbove())
pitz_prioritize_below = f(PitzPrioritizeBelow())
pitz_refresh_pickle = f(RefreshPickle(save_proj=False))
pitz_add_task = f(PitzAddTask())
pitz_add = pitz_add_task

# These scripts just read the data and report on it.
pitz_my_tasks = f(MyTasks(save_proj=False))

pitz_everything = f(PitzEverything(save_proj=False))

pitz_todo = f(
    PitzTodo(save_proj=False))

pitz_recent_activity= f(
    RecentActivity(
        script_name='pitz-recent-activity',
        doc='10 recent activities'))

pitz_tasks = f(
    PitzEverything(title="tasks", save_proj=False, type='task',
        script_name='pitz-tasks',
        doc='All tasks in the project'))

pitz_milestones = f(
    PitzEverything(title="milestones", save_proj=False,
    type='milestone', script_name='pitz-milestones',
    doc='All milestones in the project'))

pitz_statuses = f(
    PitzEverything(title="statuses", save_proj=False,
        type='status', script_name='pitz-statuses',
        doc='All statuses in the project'))

pitz_estimates = f(
    PitzEverything(title="estimates", save_proj=False,
        type='estimate', script_name='pitz-estimates',
        doc='All estimates in the project'))

pitz_components = f(
    PitzEverything(title="components", save_proj=False,
        type='component', script_name='pitz-components',
        doc='All components in the project'))

pitz_people = f(
    PitzEverything(title="people", save_proj=False,
        type='person', script_name='pitz-people',
        doc='All people in the project'))

pitz_show = f(PitzShow())

from pitz.cmdline.pitzcomment import PitzComment

pitz_comment = f(PitzComment())
