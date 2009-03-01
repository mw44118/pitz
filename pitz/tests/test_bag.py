# vim: set expandtab ts=4 sw=4 filetype=python:

import yaml

import pitz

from nose.tools import raises
from nose import SkipTest

b = pitz.Bag()

tasks = [
    pitz.Task(b, title='Clean cat box!', creator='person-matt'),
    pitz.Task(b, title='Shovel driveway', creator='person-matt'),
]

def test_matching_pairs():
    """
    Verify the bag can find all the comments.
    """

    global b, tasks

    found_tasks = b.matching_pairs([('type', 'task')])

    assert len(found_tasks) == 2

    t1, t2 = found_tasks
    assert t1['type'] == 'task'
    assert t2['type'] == 'task'

def test_new_bag():

    global tasks
    t1, t2 = tasks

    b2 = pitz.Bag(tasks)

    assert b2.entities[t1.name] == t1
    assert b2.entities[t2.name] == t2

def test_from_yaml_files_1():

    global b
    b.to_yaml_files('/home/matt/projects/pitz/pitz/junkyard/')

    b2 = pitz.Bag()

    b2.from_yaml_files(
        '/home/matt/projects/pitz/pitz/junkyard/task-*.yaml')
    
@raises(ValueError)
def test_from_yaml_files_2():

    global b
    b.to_yaml_files('/home/matt/projects/pitz/pitz/junkyard/')

    b2 = pitz.Bag()

    b2.from_yaml_files(
        '/home/matt/projects/pitz/pitz/junkyard/ditz-*.yaml')
    
