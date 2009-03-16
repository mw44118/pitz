# vim: set expandtab ts=4 sw=4 filetype=python:

import yaml

import pitz

from nose.tools import raises
from nose import SkipTest

b = pitz.Bag("Testing bag")

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
    print "len(b) is %d" % len(b)
    print "len(b.entities) is %d" % len(b.entities)

    assert len(found_tasks) == 2, "Expected 2, counted %d" % len(b)

    t1, t2 = found_tasks
    assert t1['type'] == 'task'
    assert t2['type'] == 'task'

def test_matches_dict():

    global b, tasks

    assert b.matching_pairs([('type', 'task')]).entities \
    == b.matches_dict(type='task').entities

def test_new_bag():

    global tasks
    t1, t2 = tasks

    b2 = pitz.Bag(entities=tasks)

    assert t1 in b2
    assert t2 in b2

    b.order()

def test_to_and_from_yaml_files_1():

    global b
    b.to_yaml_files('/home/matt/projects/pitz/pitz/junkyard/')

    pitz.Bag().from_yaml_files('/home/matt/projects/pitz/pitz/junkyard/')
    
def test_append_1():

    b = pitz.Bag()
    b.append(pitz.Task(title='blah'))
    
def test_values():

    b = pitz.Bag()
    b.append(pitz.Task(title='blah', difficulty='easy'))
    b.append(pitz.Task(title='blah', difficulty='hard'))

    s = b.values('difficulty')
    assert len(s) == 2
    assert 'easy' in s
    assert 'hard' in s

