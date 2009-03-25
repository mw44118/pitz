# vim: set expandtab ts=4 sw=4 filetype=python:

import yaml

import pitz

from nose.tools import raises, with_setup
from nose import SkipTest

p = None
matt = pitz.Person(title="Matt")

def setup():
    global p
    p = pitz.Project('Milestone Testing',
        entities=[
            pitz.Milestone(title="Bogus Milestone 1"),
            pitz.Milestone(title="Bogus Milestone 2"),
            pitz.Task(title='Clean cat box!', creator=matt),
            pitz.Task(title='Shovel driveway', creator=matt),
        ])

@with_setup(setup)
def test_group_tasks_into_milestones():
    """
    Verify we can put numerous tasks into milestones.
    """

    global p
    t1, t2 = p(type='task')
    m1, m2 = p(type='milestone')

    t1['milestone'] = m1.name
    t2['milestone'] = m2.name

    assert len(p(type='task', milestone=m1.name)) == 1
    assert len(p(type='task', milestone=m2.name)) == 1

@with_setup(setup)
def test_tasks_property():

    global p
    m1, m2 = p(type='milestone')
    t1, t2 = p(type='task')

    t1['milestone'] = m1.name
    t2['milestone'] = m2.name

    assert t1 in m1.tasks
    assert t2 in m2.tasks
