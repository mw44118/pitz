# vim: set expandtab ts=4 sw=4 filetype=python:

import yaml

import pitz

from nose.tools import raises
from nose import SkipTest

b = pitz.Bag(entities=[
    pitz.Task(title='Clean cat box!', creator='person-matt'),
    pitz.Task(title='Shovel driveway', creator='person-matt')])

def test_group_tasks_into_milestones():
    """
    Verify we can put numerous tasks into milestones.
    """

    global b
    t1, t2 = b
    
    m = pitz.Milestone(b, title="Bogus Milestone")

