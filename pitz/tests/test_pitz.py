# vim: set expandtab ts=4 sw=4 filetype=python:

import pitz

class Project(pitz.Blob):
    plural_name = 'projects'

class Issue(pitz.Blob):
    plural_name = 'issues'

class Person(pitz.Blob):
    plural_name = 'people'

class Milestone(pitz.Blob):
    plural_name = 'milestones'
    
class Component(pitz.Blob):
    plural_name = 'components'

def test_blob_1():
    """
    Verify Blob subclasses keep references of instances.
    """

    issues = [Issue(), Issue()]
    people = [Person(), Person()]

    assert Issue.instances == issues
    assert Person.instances == people

def test_pointers_1():

    """
    Verify we can follow pointer traits.
    """

    matt = Person()

    Issue(owner=matt, title="Wash the car")
    Issue(owner=matt, title="Take out the trash")

    x = len(matt.pointers_here['issues'])
    assert x == 2, "Counted %d, expected 2!" % x
