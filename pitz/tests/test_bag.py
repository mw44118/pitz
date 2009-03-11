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

    t1, t2 = tasks
    print "t1's type is %(type)s" % t1
    print "t1's bag is %s" % t1.bag
    print "len(b) is %d" % len(b)
    print "len(b.entities) is %d" % len(b.entities)

    assert len(found_tasks) == 2, "Expected 2, counted %d" % len(b)

    t1, t2 = found_tasks
    assert t1['type'] == 'task'
    assert t2['type'] == 'task'

def test_new_bag():

    global tasks
    t1, t2 = tasks

    b2 = pitz.Bag(entities=tasks)

    assert t1 in b2
    assert t2 in b2

def test_from_yaml_files_1():

    global b
    b.to_yaml_files('/home/matt/projects/pitz/pitz/junkyard/')

    pitz.Bag().from_yaml_files('/home/matt/projects/pitz/pitz/junkyard/')
    
