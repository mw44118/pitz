# vim: set expandtab ts=4 sw=4 filetype=python:

import jinja2

from pitz.entity import Entity

class Task(Entity):

    # This dictionary maps keys in self.data to the types they hold.
    pointers = dict(
        milestone='milestone',
        creator='person',
        owner='person',
        component='component',
    )
