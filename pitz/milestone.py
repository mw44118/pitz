# vim: set expandtab ts=4 sw=4 filetype=python:

import jinja2

from pitz.entity import Entity

class Milestone(Entity):

    """
    Milestones are groupings of tasks.

    Maybe milestones should be bags...
    """

    # This is a dictionary that maps keys in self.data to the type it
    # should hold.
    pointers = dict()

