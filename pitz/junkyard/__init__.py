# vim: set expandtab ts=4 sw=4 filetype=python:

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

        return "%(title)s (%(status)s)" % self


class Comment(Entity):
    
    required_fields = dict(
        who_said_it=None,
        text=None,
        entity=None,
        title='no title')

    pointers = ['who_said_it', 'entity']

class Person(Entity):
    pass


class PitzProject(Project):
    """
    Just like the regular project, but with some queries as properties.
    This is the project type used by pitz itself (hence the name).
    """

    # These
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
