# vim: set expandtab ts=4 sw=4 filetype=python:

"""
A bunch of experimental crap.
"""

import csv, os
from glob import glob

import yaml

class Project(yaml.YAMLObject):
    yaml_tag = u'!ditz.rubyforge.org,2008-03-06/project'

class Component(yaml.YAMLObject):
    yaml_tag = u'!ditz.rubyforge.org,2008-03-06/component'

class Release(yaml.YAMLObject):
    yaml_tag = u'!ditz.rubyforge.org,2008-03-06/release'

class Issue(yaml.YAMLObject):
    yaml_tag = u'!ditz.rubyforge.org,2008-03-06/issue'

def load_ditz_issues(where_they_live):

    """
    Give me the path to where your ditz issues are and I'll yield them
    all to you.
    """

    if not os.path.isdir(where_they_live):
        raise ValueError("Sorry, %s must be a directory.")

    for issue_file in \
    glob(os.path.join(where_they_live, 'issue-*.yaml')):    

        yield yaml.load(open(issue_file))

def to_csv(issues, csvpath):
    """
    Write out the issues to a CSV file.
    """

    w = csv.writer(open(csvpath, 'w'))
    w.writerow(['TITLE', 'STATUS'])
    for iss in issues:
        w.writerow([iss.title, iss.status])


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

