# vim: set expandtab ts=4 sw=4 filetype=python:

"""
A bunch of experimental crap.
"""

import yaml

class Project(yaml.YAMLObject):
    yaml_tag = u'!ditz.rubyforge.org,2008-03-06/project'

class Component(yaml.YAMLObject):
    yaml_tag = u'!ditz.rubyforge.org,2008-03-06/component'

class Release(yaml.YAMLObject):
    yaml_tag = u'!ditz.rubyforge.org,2008-03-06/release'

class Issue(yaml.YAMLObject):
    yaml_tag = u'!ditz.rubyforge.org,2008-03-06/issue'

# Everything below here is test code.

__test__ = dict(
    Project="""
>>> import pitz, yaml

>>> x  = yaml.load('''
... --- !ditz.rubyforge.org,2008-03-06/project 
... name: staffknex
... version: "0.5"
... components: 
... - !ditz.rubyforge.org,2008-03-06/component 
...   name: staffknex
... releases: 
... - !ditz.rubyforge.org,2008-03-06/release 
...   name: 3.5.1
...   status: :released
...   release_time: 2008-10-10 18:40:45.054912 Z
...   log_events: 
...   - - 2008-09-02 19:16:28.409034 Z
...     - Matthew Wilson <mw@staffknex.com>
...     - created
...     - Even more awesome than ever before
...   - - 2008-10-10 18:40:45.054939 Z
...     - Matthew Wilson <mw@staffknex.com>
...     - released
...     - ""
... - !ditz.rubyforge.org,2008-03-06/release 
...   name: Matt's queue
...   status: :unreleased
...   release_time: 
...   log_events: 
...   - - 2008-10-10 18:41:10.757638 Z
...     - Matthew Wilson <mw@staffknex.com>
...     - created
...     - ""
... ''')

>>> x.name
'staffknex'

>>> len(x.releases)
2
""")


class Thing(object):
    """
    Everything is usually a thing.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class Query(object):
    """
    Use queries to find subsets of things.
    """

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
