# vim: set expandtab ts=4 sw=4 filetype=python:

import logging, os
from glob import glob

import jinja2

from pitz.task import Task
from pitz.person import Person

logging.basicConfig(level=logging.INFO)

def by_whatever(*whatever):
    """
    Returns a function suitable for sorting, using whatever.

    >>> e1, e2 = {'a':1, 'b':1, 'c':2}, {'a':2, 'b':2, 'c':1}
    >>> by_whatever('a')(e1, e2)
    -1
    >>> by_whatever('c', 'a')(e1, e2)
    1
    """

    def f(e1, e2):

        return cmp(
            [e1.get(w) for w in whatever],
            [e2.get(w) for w in whatever])
        
    return f

by_spiciness = by_whatever('peppers')
by_created_time = by_whatever('created_time')

class Bag(object):
    """
    Really just a collection of entities and some functions to query
    them.
    """

    def __init__(self, pathname=None, entities=(), 
        order_method=by_created_time):

        self.entities = list(entities)
        self.pathname = pathname
        self.order_method = order_method

    def __iter__(self):
        """
        Make it possible to do "for entity in bag".
        """

        for e in self.entities:
            yield e

    def __len__(self):
        return len(self.entities)

    def reorder(self, order_method=None):

        if order_method:
            self.order_method = order_method

        if not self.order_method:
            raise ValueError("I need a method to order entities!")

        self.entities.sort(cmp=order_method)

    def matches_dict(self, **d):
        
        matches = [e for e in self if e.matches_dict(**d)]
        return self.__class__(pathname=self.pathname, entities=matches,
            order_method=self.order_method)

    def matching_pairs(self, pairs):
        """
        For pairs like

            [
                ('type', 'task'),
                ('assigned-to', 'person-matt'),
            ]

        return a new bag instance containing all entities that match.
        """

        matches = [e for e in self if e.matches_pairs(pairs)]
        return self.__class__(pathname=self.pathname, entities=matches,
            order_method=self.order_method)

    def append(self, e):
        """
        Link an entity to this bag.
        """

        # TODO: replace this O(n) scan with something better.
        if e in self.entities:
            raise ValueError("I already have %(name)s in here!" % e)

        self.entities.append(e)
        e.bag = self
        self.entities.sort(self.order_method)

    def to_yaml_files(self, pathname=None):
        """
        Tell every entity in the bag to write itself out.
        """

        if not pathname \
        and not self.pathname \
        and not os.path.isdir(self.pathname):
            raise ValueError("I need a pathname!")

        pathname = pathname or self.pathname

        return [e.to_yaml_file(pathname) 
            for e in self.entities]

    def from_yaml_files(self, pathname=None):
        """
        Loads all the files matching pathglob into this bag.
        """

        if pathname:
            self.pathname = pathname

        if not self.pathname:
            raise ValueError("I need a path to the files!")

        if not os.path.isdir(self.pathname):
            raise ValueError("%s isn't a directory." % self.pathname)

        pathglob = os.path.join(self.pathname, '*.yaml')

        for fp in glob(pathglob):

            bn = os.path.basename(fp)

            if bn.startswith('task-'):
                Task.from_yaml_file(fp, self)

            elif bn.startswith('person-'):
                Person.from_yaml_file(fp, self)

            elif bn.startswith('milestone-'):
                Milestone.from_yaml_file(fp, self)

            elif bn.startswith('component-'):
                Component.from_yaml_file(fp, self)

        return self
                
    def __str__(self):

        # First reorder the entitities.
        self.entities.sort(self.order_method)
        
        t = jinja2.Template("""\
{% for e in entities -%}
    {{e.summarized_view}}
{% endfor %}""")

        return t.render(entities=self)
