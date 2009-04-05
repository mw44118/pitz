# vim: set expandtab ts=4 sw=4 filetype=python:

from pitz.entity import Entity

class Comment(Entity):
    
    required_fields = dict(
        who_said_it=None,
        text=None,
        entity=None)

    pointers = ['who_said_it', 'entity']
