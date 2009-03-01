# vim: set expandtab ts=4 sw=4 filetype=python:

import logging
from UserDict import UserDict
from datetime import datetime
import os

import hashlib, random

import yaml

import jinja2

class Entity(UserDict):
    """
    A regular dictionary with a few extra tweaks.
    """

    required_fields = ['title', 'creator']

    def __init__(self, bag=None, **kwargs):

        """
        At least needs title and creator in kwargs.
        """

        for rf in self.required_fields:
            if rf not in kwargs:
                raise ValueError("I need these required fields %s" 
                    % self.required_fields)

        UserDict.__init__(self, **kwargs)
        self.data['type'] = self.__class__.__name__.lower()

        # Make a name if it wasn't provided.
        if 'name' not in kwargs:
            a = str(datetime.now())
            b = str(random.random())
            c = hashlib.sha1(a+b).hexdigest()

            self['name'] = '%s-%s' % (self.data['type'], c)

        # Handle attributes with defaults.
        if 'created_date' not in kwargs:
            self.data['created_date'] = datetime.now() 

        if 'modified_date' not in kwargs:
            self['modified_date'] = self.data['created_date']

        if 'last_modified_by' not in kwargs:
            self.data['last_modified_by'] = self.data['creator']
        
        if 'description' not in kwargs:
            self.data['description'] = self.data['title']

        # Finally, add this entity to the bag (if we got one).
        if bag:
            self.bag = bag
            self.bag.append(self)

    @property
    def name(self):
        return self.data['name']

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
        return "%s(%s)" % (self.__class__.__name__, self.data)

    @property
    def plural_view(self):
        """
        This is what the entity looks like when it is one of many
        things.
        """

        return "%(name)-10s: %(title)s" % self.data

    @property
    def singular_view(self):
        """
        The detailed view.
        """

        d = dict()
        d.update(self.data)
        d['plural_view'] = self.plural_view
        d['line_of_dashes'] = "-" * len(self.plural_view)
        d['type'] = self.__class__.__name__

        t = jinja2.Template("""\
{{plural_view}}
{{line_of_dashes}}

            type: {{type}}
            name: {{name}}
           title: {{title}}
     description: {{description}}
    created date: {{created_date}}
   modified date: {{modified_date}}
         creator: {{creator}}
last modified by: {{last_modified_by}}

Comments:
{% for c in comments %}
  {{c}}
{% endfor %}
""")
        
        return t.render(**d)

    def __str__(self):
        return self.plural_view

    @property
    def yaml(self):
        return yaml.dump(self.data, default_flow_style=False)

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

    @classmethod
    def from_yaml_file(cls, bag, fp):
        """
        Loads the file at file path fp into the bag and returns it.
        """

        d = yaml.load(open(fp))
        return cls(bag, **d)
