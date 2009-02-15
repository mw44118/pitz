# vim: set ts=4 sw=4 filetype=python:

from collections import defaultdict

import yaml

class Blob(yaml.YAMLObject):

    @property
    def id(self):
        return id(self)

    @property
    def type(self):
        return type(self)

    def __new__(cls, *args, **kwargs):
        """
        I'm doing this so every instance can add itself to the list of
        instances.

        Remember that if I put the instances attribute on the class,
        then all subclasses would get a reference to it.
        """


        if not hasattr(cls, 'instances'):
            cls.instances = []

        self = super(Blob, cls).__new__(cls)
        cls.instances.append(self)
        self.pointers_here = defaultdict(list)

        return self

    def __init__(self, **kwargs):
        """
        Any keyword params are added as traits.
        """

        for k,v  in kwargs.items():

            setattr(self, k, v)

            if isinstance(v, Blob):

                plural_name = self.__class__.plural_name
                v.pointers_here[plural_name].append(self)

    def __repr__(self):

        attributes = ', '.join(['%s=%s' % (k, v) 
            for k, v in self.__dict__.items()
            if k not in ('pointers_here', )])

        return "%s(%s)" % (self.__class__.__name__, attributes)
    
class EAV(object):
    """
    crappy implementation of entity-attribute-value database.
    """

    def __init__(self, tl):
        """
        tl needs to be a list of tuples like
            ('entity', 'attribute', 'value')
        """
        self.tl = tl

    @property
    def types(self):
        """
        Return a set of all types defined in this database.
        """

        return set([t[2] for t in self.tl if t[1] == 'type'])

    def matching_pairs(self, pairs):
        """
        For pairs like

            [
                ('type', 'task'),
                ('assigned-to', 'person-matt'),
            ]

        return all entities that match.
        """
    
class Entity(object):
    """
    Just a primitive bag of attributes and values, with some other
    stupid stuff mixed in.
    """

    def __init__(self, tl):
        """
        tl mustt be a list of (entity, attribute, value) tuples, and all
        the entity elements have to be the same.
        """
