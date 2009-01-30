# vim: set ts=4 sw=4 filetype=python:

"""
Python interface to ditz (http://ditz.rubyforge.org)
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
