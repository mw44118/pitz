# vim: set expandtab ts=4 sw=4 filetype=python:

"""
Verify the stuff in simplepitz works.
"""

import glob, unittest

from uuid import uuid4, UUID

from nose.tools import raises, with_setup

from pitz.exceptions import NoProject

from pitz.bag import *

p = None

def setup():

    global p
    p = Project()
    p.append(Task(title='Draw new accounting report', priority=2))
    p.append(Task(title='Improve speed of search page', priority=0))

    p.append(Task(title='Add animation to site logo',
        estimate=Estimate(title="straightforward", points=2)))

    p.append(Task(title='Write "forgot password?" feature',
        priority=1, estimate=Estimate(title="straightforward", points=2)))

    p.append(Task(title='Allow customer to change contact information',
        priority=2, estimate=Estimate(title="straightforward", points=2)))

    p.append(Task(title='Allow customer to change display name',
        priority=2, estimate=Estimate(title="easy", points=1)))

    p.append(Milestone(title="1.0"))
    p.append(Milestone(title="2.0"))

@raises(NoProject)
def test_noproject():
    m = Milestone(title="Bogus milestone")
    m.tasks

def test_show_milestones():
    """
    List every milestone.
    """

    global p

    for m in p.milestones:
        m.todo
    
def test_milestone_todo():
    
    global p

    for m in p.milestones:
        m.todo

def test_milestone_summarized_view():

    global p

    for m in p.milestones:
        m.summarized_view


def test_comments():

    global p
    t = Task(p, title="wash dishes")
    z = Comment(p, entity=t, title="I don't want to", who_said_it="Matt")
    c = t.comments[0]
    c.summarized_view
    c.detailed_view

def test_project_todo():

    global p
    p.todo


def test_project_tasks():

    global p
    p.tasks

def test_project_people():

    global p
    p.people

def test_project_comments():

    global p
    p.comments

def test_unscheduled():

    global p
    p.unscheduled


def test_abandon_task():
    
    global p
    t = Task(p, title="wash dishes")
    t.abandon()

@raises(NoProject)
def test_component():

    c1 = Component(title="Component A")
    c1.tasks

def test_components_property():

    global p
    c1 = Component(p, title="Component A")
    assert p.components.length == 1, p.components
    assert c1 in p.components

def test_started_property():

    global p
    started_tasks = p(type='task', status='started')
    assert p.started.length == started_tasks.length


def test_from_uid():
    """
    Use the os.getuid() to look up a person.
    """

    matt = Person(
        title='W. Matthew Wilson')


def test_repr_after_replace_objects_with_pointers():


    p = Project(
        entities=[
            Task(title="wash dishes",
                status=Status(title="unstarted"))])

    t = Task(title="wash dishes")
    assert t in p

    assert isinstance(t['status'], Entity)
    t.replace_objects_with_pointers()
    assert isinstance(t['status'], UUID)

    t.summarized_view
