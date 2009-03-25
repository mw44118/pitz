# vim: set expandtab ts=4 sw=4 filetype=python:

from copy import copy
import logging
from UserDict import UserDict
from datetime import datetime
import os, uuid

import yaml

import jinja2

from pitz.exceptions import NoProject

logging.basicConfig(level=logging.INFO)

class Entity(UserDict):
    """
    A regular dictionary with a few extra tweaks.
    """

    required_fields = ['title']
    pointers = dict()

    def __init__(self, project=None, **kwargs):

        # First set up a few instance variables.
        self.comments = []

        # Now make sure we got all the required fields.
        for rf in self.required_fields:
            if rf not in kwargs:
                raise ValueError("I need these required fields %s" 
                    % self.required_fields)

        UserDict.__init__(self, **kwargs)
        self.data['type'] = self.__class__.__name__.lower()

        # Make a name if it wasn't provided.
        if 'name' not in kwargs:
            self['name'] = '%s-%s' % (self.data['type'], uuid.uuid4())

        # Handle attributes with defaults.
        if 'created_time' not in kwargs:
            self.data['created_time'] = datetime.now() 

        if 'modified_time' not in kwargs:
            self['modified_time'] = self.data['created_time']

        # Add this entity to the project (if we got a project).
        self.project = project
        if project is not None:
            self.project.append(self)

    @property
    def comments(self):
        return self.comments

    @property
    def name(self):
        return self.data['name']

    @property
    def as_eav_tuples(self):
        return [(self.data['name'], a, v) 
        for a, v in self.data.items() 
        if a != 'name']

    def matches_pairs(self, pairs):

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

    def matches_dict(self, **d):
        """
        Just like self.matches_pairs, except accepts keyword args.

        >>> e = Entity(title='Clean cat box', creator='Matt')
        >>> e == e.matches_dict(creator='Matt')
        True
        >>> None == e.matches_dict(creator='Nobody')
        True
        """

        for a, v in d.items():

            if isinstance(v, (list, tuple)):
                raise TypeError("Sorry, values can't be lists (yet)")

            if a not in self.data or self.data[a] != v:
                return

        return self

    def __repr__(self):
        return "<pitz.%s object '%s'>" \
        % (self.__class__.__name__, self['title'])

    @property
    def summarized_view(self):
        """
        Short description of the entity.
        """

        return "%(title)s (%(type)s)" % self

    @property
    def detailed_view(self):
        """
        The detailed view of the entity.
        """

        d = dict()
        d.update(self.data)
        d['summarized_view'] = self.summarized_view
        d['line_of_dashes'] = "-" * len(self.summarized_view)
        d['type'] = self.__class__.__name__

        t = jinja2.Template("""\
{{summarized_view}}
{{line_of_dashes}}

description: 
{{description}}

All fields:
{% for k in data %}
{{ k }}:
{{ data[k] }}
{% endfor %}
""")

        return t.render(**d)


    def __str__(self):
        return self.summarized_view

    @property
    def yaml(self):

        self.replace_objects_with_pointers()

        y = yaml.dump(self.data, default_flow_style=False)

        # Now switch the pointers with the objects.
        if self.project:
            self.replace_pointers_with_objects()

        return y

    def to_yaml_file(self, pathname):
        """
        Returns the path of the file saved.

        The pathname specifies where to save it.
        """

        fp = os.path.join(pathname, '%s.yaml' % (self.name)) 
        f = open(fp, 'w')
        f.write(self.yaml)
        f.close()
        logging.debug("Saved file %s" % fp)

        return fp

    def replace_pointers_with_objects(self):

        """
        Replace pointer to entities with the entities that are pointed
        to.

        In other words, replaces the string "matt" with the object with
        "matt" as its name.
        """

        if not self.project:
            raise NoProject("I need a project first!")

        for p in self.pointers:
            if p in self:
                self[p] = self.project.by_name(self[p])


    def replace_objects_with_pointers(self):
        """
        Replaces the value of an entity with just the string of the
        entity's name.

        In other words, replaces the object stored at sef['creator']
        with just the name of that object.
        """

        for p in self.pointers:
            if p in self:
                o = self[p]

                # Remember that all subclasses of Entity will return
                # True for isinstance(o, Entity).
                if isinstance(o, Entity):
                    self[p] = o.name

    def comment(self, who_said_it, what_they_said, when_they_said_it='right now'):

        if when_they_said_it == 'right now':
            when_they_said_it = datetime.now()
        
        self.comments.append(
            (who_said_it, when_they_said_it, what_they_said))


    @classmethod
    def from_yaml_file(cls, fp, project=None):
        """
        Loads the file at file path fp into the project and returns it.
        """

        d = yaml.load(open(fp))

        if not d:
            return

        e = cls(project, **d)

        # If we have a project, try to replace literals with pointers.
        if project:
            e.replace_pointers_with_objects()

        return e
