# vim: set expandtab ts=4 sw=4 filetype=python:

"""\
Like trac (http://trac.edgewall.org) with tasks bundled into milestones.
"""

from copy import copy

import jinja2

from pitz.entity import Entity
from pitz.project import Project
from pitz.exceptions import NoProject

class Milestone(Entity):

    @property
    def tasks(self):

        if not self.project:
            raise NoProject("I need a project before I can look up tasks!")

        tasks = self.project(type='task', milestone=self)
        tasks.title = 'Tasks in %(title)s' % self
        return tasks

    @property
    def todo(self):

        unfinished = self.tasks.does_not_match_dict(status='finished')\
        .does_not_match_dict(status='abandoned')

        unfinished.title = "Unfinished tasks in %(title)s" % self
        return unfinished
        

class Task(Entity):

    required_fields = dict(
        milestone='unscheduled',
        title='no title',
        status='unstarted')

    allowed_values = dict(
        status=['unstarted', 'started', 'abandoned', 'finished'],
    )

    pointers = ['milestone', 'person', 'component']

    @property
    def summarized_view(self):
        """
        Short description of the task.
        """

        return "%(namefrag)s %(title)s (%(status)s)" % self

    @property
    def comments(self):
        """
        Return all comments on this task.
        """
    
        b = self.project(type='comment', entity=self)
        b.title = 'Comments on %(title)s' % self
        return b


class Comment(Entity):
    
    required_fields = dict(
        who_said_it=None,
        text=None,
        entity=None,
        title='no title')

    pointers = ['who_said_it', 'entity']

    @property
    def summarized_view(self):

        t = self['text'].strip().replace('\n', ' ')
        
        return "%(author)s at %(time)s said: %(text)s" % dict(
            author=self['who_said_it']['title'],
            time=self['created_time'].strftime("%I:%M %P, %a, %m/%d/%y"),
            text="%s..." % t[:60] if len(t) > 60 else t,
        )

class Person(Entity):
    pass


class PitzProject(Project):
    """
    Just like the regular project, but with some queries as properties.
    This is the project type used by pitz itself (hence the name).
    """

    # These are all the classes I deal with.
    classes = dict(
        task=Task,
        person=Person,
        milestone=Milestone,
        comment=Comment)

    @property
    def todo(self):
        b = self(type='task').does_not_match_dict(status='finished')
        b.title = 'Stuff to do'
        return b

    # I know I COULD make all these properties in the __init__ method
    # based on the classes dictionary, but this way is hopefully much
    # more obvious and solves the hassle of indicating that the plural
    # of "person" is "people".
    @property
    def milestones(self):
        b = self(type='milestone')
        b.title = 'Milestones'
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
    def unscheduled(self):
        """
        Unfinished tasks not linked to any milestones.
        """

        b = self(type='task').does_not_match_dict(status='finished')

        for m in self.milestones:
            b = b.does_not_match_dict(milestone=m)

        b.title = 'Unscheduled and unfinished tasks'
        return b
