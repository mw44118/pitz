# vim: set ts=4 sw=4 filetype=python:

from UserDict import UserDict
import yaml

class Entity(UserDict):
    """
    A regular dictionary with a few extra tweaks.
    """
    
    def __init__(self, d=None, **kwargs):
        """
        Make sure we get at least an entity attribute, a title, and a
        type.
        """

        UserDict.__init__(self, d, **kwargs)

        for a in ('entity', 'title', 'type'):
            if a not in self.data:
                raise ValueError("I need an attribute named %s!" % a)

    @property
    def as_eav_tuples(self):
        return [(self.data['entity'], a, v) 
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

    @property
    def plural_view(self):
        """
        This is what the entity looks like when it is one of many
        things.
        """

        return "%(entity)-10s: %(title)s" % self.data

    def __str__(self):
        return self.plural_view

    @property
    def attribute_block(self):

        pretty_attributes = []

        for a, v in self.data.items():
            if isinstance(v, (list, tuple)):
                pretty_attributes += [""]
                pretty_attributes += ["%s:" % a]
                for x in v:
                    pretty_attributes += [' ' * 4 + str(x)]
                pretty_attributes += [""]
                
            else:
                pretty_attributes += ["%s: %s" % (a, v)]

        return "\n".join(pretty_attributes)

    @property 
    def singular_view(self):
        """
        The detail view.
        """

        h1 = "%(type)s: %(title)s" % self.data
        plusline = "+" * len(h1)
        attribute_block = self.attribute_block

        return """\
%(plusline)s
%(h1)s
%(plusline)s

%(attribute_block)s

""" % locals()

class Bag(object):
    """
    Really just a collection of entities and some functions to query
    them.
    """

    def __init__(self, entities=None):
        
        self.entities = {}
        for e in entities:
            self.entities[e.entity] = e

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
