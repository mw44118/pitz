# vim: set expandtab ts=4 sw=4 filetype=python:

import logging, os
from glob import glob

import jinja2

from pitz.task import Task

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

        return a new bag instance containing all entities that match.
        """

        matches = [e for e in self.entities.values() if e.match(pairs)]
        return self.__class__(matches)

    def append(self, e):
        """
        Link an entity to this bag.
        """

        if e['name'] in self.entities:
            raise ValueError("I already have %(name)s in here!" % e)

        self.entities[e['name']] = e
        e.bag = self

    def to_yaml_files(self, pathname):
        """
        Tell every entity in the bag to write itself out.
        """

        return [e.to_yaml_file(pathname) for e in self.entities.values()]

    def from_yaml_files(self, pathglob):
        """
        Loads all the files matching pathglob into this bag.

        >>> b = Bag()
        >>> b.from_yaml_files('/tmp/task-*.yaml')
        """

        for fp in glob(pathglob):
            bn = os.path.basename(fp)
            if bn.startswith('task-'):
                t = Task.from_yaml_file(self, fp)
            else:
                raise ValueError("I can't parse %s yet." % bn)
                
    def __str__(self):
        
        t = jinja2.Template("""\
{% for e in entities %}
    {{e.plural_view}}
{% endfor %}""")

        return t.render(entities=self.entities.values())
