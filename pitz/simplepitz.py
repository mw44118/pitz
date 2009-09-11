# vim: set expandtab ts=4 sw=4 filetype=python:

"""
Simple projects have tasks, people, comments, components, and
milestones.
"""

myclassname = 'SimpleProject'

from copy import copy
import logging, os, pwd, socket, textwrap

import clepy, jinja2, yaml

from pitz import by_created_time
from pitz.entity import Entity
from pitz.project import Project
from pitz.exceptions import NoProject

log = logging.getLogger('pitz.simplepitz')


class Estimate(Entity):

    required_fields = dict(points='???')

    def __str__(self):
        return self.title

    @property
    def tasks(self):
        """
        Return tasks with this estimate.
        """

        if not self.project:
            raise NoProject("Need a self.project for this!")

        else:
            return self.project.tasks(estimate=self)


class Status(Entity):

    def __str__(self):
        return self.title

    @property
    def tasks(self):
        """
        Return tasks with this status
        """

        if not self.project:
            raise NoProject("Need a self.project for this!")

        else:
            return self.project.tasks(status=self)


class Milestone(Entity):
    """
    Useful for bundling tasks
    """

    plural_name = "milestones"

    @property
    def tasks(self):

        if not self.project:
            raise NoProject("I need a project before I can look up tasks!")

        tasks = self.project(type='task', milestone=self)
        tasks.title = 'Tasks in %(title)s' % self
        return tasks

    @property
    def todo(self):

        unfinished = self.tasks.does_not_match_dict(
            status=Status(title='finished'))\
        .does_not_match_dict(status=Status(title='abandoned'))

        unfinished.title = "Unfinished tasks in %(title)s" % self
        return unfinished

    @property
    def summarized_view(self):

        finished = Status(title='finished')

        a = self.tasks(status=finished).length
        b = self.tasks.length

        if b is not 0:
            pct_complete = 100*(float(a)/b)
        else:
            pct_complete = 0.0

        d = {
            'frag':self['frag'],
            'title':self['title'],
            'pct_complete':pct_complete,
            'num_finished_tasks':a,
            'num_tasks': b}

        s = "%(frag)s %(title)s: %(pct_complete)0.0f%% complete (%(num_finished_tasks)d / %(num_tasks)d tasks)"
        return s % d


class Task(Entity):

    plural_name = "tasks"

    allowed_types = dict(
        milestone=Milestone,
        status=Status,
        estimate=Estimate)

    required_fields = dict(
        title=None,
        description='',
        milestone=lambda proj: Milestone(proj, title='unscheduled'),
        status=lambda proj: Status(proj, title='unstarted'),
        estimate=lambda proj: Estimate(proj, title='not estimated', points=None),
        components=lambda proj: list(),
        comments=lambda proj: list(),
    )


    @property
    def milestone(self):
        return self['milestone']


    @property
    def status(self):
        return self['status']


    @property
    def estimate(self):
        return self['estimate']


    @property
    def summarized_view(self):
        """
        Short description of the task.
        """

        frag = self['frag']
        title = clepy.maybe_add_ellipses(self.title, 45)

        status = '(%s)' % getattr(self['status'], 'abbr', self['status'])

        if 'milestone' in self:
            milestone = getattr(self['milestone'], 'abbr', self['milestone'])
        else:
            milestone = '...'

        pscore = self['pscore']

        return "%(frag)6s  %(title)-48s  %(milestone)3s  %(status)-11s" \
        % locals()


    @property
    def comments(self):
        """
        Return all comments on this task.
        """

        b = self.project(type='comment', entity=self)
        b.title = 'Comments on %(title)s' % self

        return b.order(by_created_time)


    def abandon(self):

        if self['status'].title in ['unstarted', 'started']:
            self['status'] = Status(title='abandoned')
            return self

        else:
            raise ValueError('You can only abandon unstarted or started tasks.')


    def start(self):

        if self['status'].title in ['unstarted', 'abandoned']:
            self['status'] = Status(title='started')
            return self

        else:
            raise ValueError('You can only start unstarted or abandoned tasks.')


    def finish(self):

        if self['status'].title == 'started':
            self['status'] = Status(title='finished')
            return self

        else:
            raise ValueError('You can only finish started.')


class Comment(Entity):

    """
    You can comment on any entity.
    """

    plural_name = "comments"

    required_fields = dict(
        who_said_it=None,
        title=None,
        entity=None)

    @property
    def summarized_view(self):

        title = self['title'].strip().replace('\n', ' ')
        title = "%s..." % title[:60] if len(title) > 60 else title

        who_said_it = self['who_said_it']
        who_said_it = getattr(who_said_it, 'title', who_said_it)

        return "%(who_said_it)s said: %(title)s" % dict(
            who_said_it=who_said_it,
            time=self['created_time'].strftime("%I:%M %P, %a, %m/%d/%y"),
            title=title,
        )


    @property
    def detailed_view(self):

        title = textwrap.fill(self['title'].strip().replace('\n', '  '))

        who_said_it = self['who_said_it']
        who_said_it = getattr(who_said_it, 'title', who_said_it)

        time = self['created_time'].strftime("%A, %B %d, %Y, at %I:%M %P")

        tmpl = self.e.get_template('comment_detailed_view.txt')

        return tmpl.render(locals())


class Person(Entity):
    """
    Maybe you want to track who is doing what.
    """

    plural_name = "people"




    def save_as_me_yaml(self):

        """
        Designate this person is me by saving a me.yaml file.
        """

        if not self.project:
            raise NoProject("Sorry, saving a me.yaml needs a project")

        me_yaml_path = os.path.join(self.project.pathname, 'me.yaml')
        me_yaml = open(me_yaml_path, 'w')
        me_yaml.write(yaml.dump(self.uuid))

        return me_yaml_path



class Component(Entity):

    plural_name = "components"

    @property
    def tasks(self):

        if not self.project:
            raise NoProject("I need a project before I can look up tasks!")

        tasks = self.project(type='task', milestone=self)
        tasks.title = 'Tasks in %(title)s' % self

        return tasks

    @property
    def todo(self):

        unfinished = self.tasks.does_not_match_dict(
            status=Status(title='finished'))\
        .does_not_match_dict(status=Status(title='abandoned'))

        unfinished.title = "Unfinished tasks in %(title)s" % self
        return unfinished


class SimpleProject(Project):
    """
    Just like the regular project, but with some queries as properties.
    """


    def __init__(self, *args, **kwargs):

        super(SimpleProject, self).__init__(*args, **kwargs)
        self.find_me()


    # These are all the classes I deal with.
    classes = dict(
        status=Status,
        estimate=Estimate,
        task=Task,
        person=Person,
        milestone=Milestone,
        comment=Comment,
        component=Component)

    @property
    def todo(self):

        b = self(type='task')\
        .does_not_match_dict(status=Status(title='finished'))\
        .does_not_match_dict(status=Status(title='abandoned'))

        b.title = '%s: stuff to do' % self.title
        return b

    # TODO: replace all these properties with some metaclass tomfoolery.
    @property
    def milestones(self):
        b = self(type='milestone')
        b.title = 'Milestones'
        return b

    @property
    def components(self):
        b = self(type='component')
        b.title = 'Components'
        return b

    @property
    def tasks(self):
        b = self(type='task')
        b.title = 'Tasks'
        return b

    @property
    def people(self):
        b = self(type='person')
        b.title = 'People'
        return b

    @property
    def comments(self):
        b = self(type='comment')
        b.title = 'Comments'
        return b

    @property
    def estimates(self):
        b = self(type='estimate')
        b.title = 'Estimates'
        return b

    @property
    def statuses(self):
        b = self(type='status')
        b.title = 'Statuses'
        return b

    @property
    def unscheduled(self):
        """
        Unfinished tasks not linked to any milestones.
        """

        b = self(type='task').does_not_match_dict(status='finished')

        for m in self.milestones:
            b = b.does_not_match_dict(milestone=m)

        b.title = 'Unscheduled and unfinished tasks'
        return b


    @property
    def started(self):
        b = self(type='task', status='started')
        b.title = 'Started tasks'
        return b


    def find_me(self):

        """
        Return the person currently using this pitz session by reading
        the pitzdir/you.yaml file.
        """


        # When no people have been created, there's no point.
        if not self.people:
            return

        if hasattr(self, 'current_user'):
            return self.current_user

        pitzdir = self.pathname
        me_yaml = os.path.join(pitzdir, 'me.yaml')

        if not os.path.isfile(me_yaml):
            return
        
        self.current_user = self[yaml.load(open(me_yaml))]
        return self.current_user
