# vim: set ts=4 sw=4 filetype=python:

from UserDict import UserDict
from datetime import datetime

import yaml

class Bag(object):
    """
    Really just a collection of entities and some functions to query
    them.
    """

    def __init__(self, entities=()):
        
        self.entities = {}
        for e in entities:
            self.entities[e['name']] = e

    def matching_pairs(self, pairs):
        """
        For pairs like

            [
                ('type', 'task'),
                ('assigned-to', 'person-matt'),
            ]

        return all entities that match.
        """

        return [e for e in self.entities.values() if e.match(pairs)]

class Entity(UserDict):
    """
    A regular dictionary with a few extra tweaks.
    """

    def __init__(self, d=None, created_date="right now",
        description="same as title", **kwargs):

        """
        Make sure we get at least the required attributes.
        """

        UserDict.__init__(self, d, **kwargs)

        for a in ('name', 'title', 'creator', 'type'):

            if a not in self.data:
                raise ValueError("I need an attribute named %s!" % a)

        # Now set up the attributes that have defaults.
        if created_date == "right now":
            created_date = datetime.now() 

        self.data['created_date'] = self.data['modified_date'] \
        = created_date

        self.data['last_modified_by'] = self.data['creator']
        
        if description == "same as title":
            description = self.data['title']

        self.data['description'] = description

    @property
    def as_eav_tuples(self):
        return [(self.data['name'], a, v) 
        for a, v in self.data.items() 
        if a != 'name']
    
    def match(self, pairs):

        """
        Return self or None, depending on whether this entity matches
        everything in the pairs.
        """

        for a, v in pairs:
            
            if isinstance(v, (list, tuple)):
                raise TypeError("Sorry, values can't be lists (yet)")

            if a not in self.data or self.data[a] != v:
                return

        return self

    def __repr__(self):
        return "%s(%s)" % (self.__class__, self.data)

    @property
    def plural_view(self):
        """
        This is what the entity looks like when it is one of many
        things.
        """

        return "%(name)-10s: %(title)s" % self.data

    def __str__(self):
        return self.plural_view

class Task(Entity):

    def singular_view(self, bag):

        return self.plural_view

