# vim: set expandtab ts=4 sw=4 filetype=python:

import logging, os
from glob import glob

import jinja2

from pitz.task import Task

logging.basicConfig(level=logging.INFO)

class Bag(object):
    """
    Really just a collection of entities and some functions to query
    them.
    """

    def __init__(self, pathname=None, entities=()):

        self.entities = {}
        self.pathname = pathname

        if pathname:
            
            if not os.path.isdir(pathname):
                raise ValueError("%s isn't a directory." % pathname)

            self.from_yaml_files(pathname)
        
        for e in entities:
            self.entities[e['name']] = e

    def __iter__(self):
        """
        Make it possible to do "for entity in bag".
        """

        for e in self.entities.values():
            yield e

    def __len__(self):
        return len(self.entities)

    def matching_pairs(self, pairs):
        """
        For pairs like

            [
                ('type', 'task'),
                ('assigned-to', 'person-matt'),
            ]

        return a new bag instance containing all entities that match.
        """

        matches = [e for e in self.entities.values() if e.match(pairs)]
        return self.__class__(entities=matches)

    def append(self, e):
        """
        Link an entity to this bag.
        """

        if e['name'] in self.entities:
            raise ValueError("I already have %(name)s in here!" % e)

        self.entities[e['name']] = e
        e.bag = self

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
            for e in self.entities.values()]

    def from_yaml_files(self, pathname):
        """
        Loads all the files matching pathglob into this bag.
        """

        # Later on, I'll load in more files.
        pathglob = os.path.join(pathname, 'task-*.yaml')

        for fp in glob(pathglob):
            t = Task.from_yaml_file(fp, self)
                
    def __str__(self):
        
        t = jinja2.Template("""\
{% for e in entities -%}
    {{e.plural_view}}
{% endfor %}""")

        return t.render(entities=self)
