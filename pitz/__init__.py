# vim: set ts=4 sw=4 filetype=python:

from UserDict import UserDict
import yaml
    
class EAV(object):
    """
    Really just a collection of entities and some functions to query
    them.
    """

    def matching_pairs(self, pairs):
        """
        For pairs like

            [
                ('type', 'task'),
                ('assigned-to', 'person-matt'),
            ]

        return all entities that match.
        """



class Entity(UserDict):
    """
    A regular dictionary with a few extra tweaks.
    """
    
    def __init__(self, d=None, **kwargs):
        """
        Make sure we get an entity attribute.
        """

        UserDict.__init__(self, d, **kwargs)

        if 'entity' not in self.data:
            raise ValueError("I need an entity attribute!")

    @property
    def entity(self):
        return self.data['entity']

    @property
    def as_eav_tuples(self):
        return [(self.entity, a, v) 
        for a, v in self.data.items() 
        if a != 'entity']
    
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
