# vim: set expandtab ts=4 sw=4 filetype=python:

from pitz.entity import Entity

class Task(Entity):

    # This is a dictionary that maps keys in self.data to the type it
    # should hold.
    pointers = dict(
        milestone='milestone',
        creator='person',
        owner='person',
        component='component',
    )
