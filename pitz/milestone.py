# vim: set expandtab ts=4 sw=4 filetype=python:

import jinja2

from pitz.entity import Entity
from pitz.exceptions import NoProject

class Milestone(Entity):

    """
    Milestones are groupings of tasks.

    Maybe milestones subclass bags...
    """

    # This is a dictionary that maps keys in self.data to the type it
    # should hold.
    pointers = dict()

    @property
    def tasks(self):

        if not self.project:
            raise NoProject("I need a project before I can look up tasks!")

        return self.project(type='task', milestone=self.name)
