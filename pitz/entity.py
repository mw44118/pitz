# vim: set expandtab ts=4 sw=4 filetype=python:

import logging
from UserDict import UserDict
from datetime import datetime

import hashlib, random

import yaml

import jinja2

class Entity(UserDict, yaml.YAMLObject):
    """
    A regular dictionary with a few extra tweaks.
    """

    def __init__(self, bag, created_date="right now",
        description="same as title", **kwargs):

        """
        Make sure we get at least the required attributes.
        """

        UserDict.__init__(self, **kwargs)

        # Verify we got all the keys we want.
        for a in ('title', 'creator'):

            if a not in self.data:
                raise ValueError("I need an attribute named %s!" % a)


        # Make a name attribute.
        a = str(datetime.now())
        b = str(random.random())
        c = hashlib.sha1(a+b).hexdigest()

        self['name'] = '%s-%s' % (self.__class__.__name__.lower(), c)

        # Now set up the attributes that have defaults.
        if created_date == "right now":
            created_date = datetime.now() 

        self.data['created_date'] = self.data['modified_date'] \
        = created_date

        self.data['last_modified_by'] = self.data['creator']
        
        if description == "same as title":
            description = self.data['title']

        self.data['description'] = description

        # Finally, add ourself to the bag.
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
        return yaml.dump(self, default_flow_style=False)

    def to_yaml_file(self):
        """
        Returns the path of the file saved.
        """

        fp = '/home/matt/projects/pitz/pitz/junkyard/%s.yaml' \
        % (self.name) 

        f = open(fp, 'w')

        f.write(self.yaml)

        f.close()

        logging.debug("Saved file %s" % fp)

        return fp

    @classmethod
    def from_yaml_file(cls, fp):
        """
        Loads the file at file path fp and returns it.
        """

        return cls.load(open(fp))
    
    @classmethod
    def load(cls, document):
        obj = yaml.load(document)
        assert isinstance(obj, cls)
        return obj


        



