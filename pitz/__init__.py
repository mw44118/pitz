# vim: set ts=4 sw=4 filetype=python:

import yaml

class Project(yaml.YAMLObject):
    yaml_tag = u'ditz.rubyforge.org,2008-03-06/project'

class Component(yaml.YAMLObject):
    yaml_tag = u'ditz.rubyforge.org,2008-03-06/component'

class Release(yaml.YAMLObject):
    yaml_tag = u'ditz.rubyforge.org,2008-03-06/release'

class Issue(yaml.YAMLObject):
    yaml_tag = u'ditz.rubyforge.org,2008-03-06/issue'

"""
These are all the ditz types I know of.

!ditz.rubyforge.org,2008-03-06/project 
!ditz.rubyforge.org,2008-03-06/component 
!ditz.rubyforge.org,2008-03-06/release 
!ditz.rubyforge.org,2008-03-06/issue 
"""
