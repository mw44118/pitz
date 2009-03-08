# vim: set expandtab ts=4 sw=4 filetype=python:

import logging, os
from glob import glob

import jinja2

from pitz.task import Task

logging.basicConfig(level=logging.INFO)

def by_created_time(e1, e2):
    "Orders entities by created time."

    return cmp(e1['created_time'], e2['created_time'])

def by_creator(e1, e2):
    "Orders entities by creator."

    return cmp(e1['creator'], e2['creator'])

def by_spiciness(e1, e2):
    "Looks at the number of peppers on each entity."

    return cmp(e1.get('peppers', 99), e2.get('peppers', 99))

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

        if pathname:
            
            if not os.path.isdir(pathname):
                raise ValueError("%s isn't a directory." % pathname)

            self.from_yaml_files(pathname)

        if self.order_method:
            self.entities.sort(cmp=order_method)


    def __iter__(self):
        """
        Make it possible to do "for entity in bag".
        """

        for e in self.entities:
            yield e

    def __len__(self):
        return len(self.entities)

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

    def from_yaml_files(self, pathname):
        """
        Loads all the files matching pathglob into this bag.
        """

        # Later on, I'll load in more files.
        pathglob = os.path.join(pathname, 'task-*.yaml')

        for fp in glob(pathglob):
            t = Task.from_yaml_file(fp, self)
                
    def __str__(self):

        # First reorder the entitities.
        self.entities.sort(self.order_method)
        
        t = jinja2.Template("""\
{% for e in entities -%}
    {{e.summarized_view}}
{% endfor %}""")

        return t.render(entities=self)
