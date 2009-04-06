# vim: set expandtab ts=4 sw=4 filetype=python:

import yaml

import pitz

from nose.tools import raises
from nose import SkipTest

b = pitz.Bag("Testing bag")

tasks = [

    pitz.Task(b, title='Clean cat box!', creator='person-matt',
        status='really important'),

    pitz.Task(b, title='Shovel driveway', creator='person-matt',
        status='not very important'),
]

def test_matches_dict():

    global b, tasks
    b.matches_dict(type='task')

def test_new_bag():

    global tasks
    t1, t2 = tasks

    b2 = pitz.Bag(entities=tasks)

    assert t1 in b2
    assert t2 in b2

    b.order()

def test_to_and_from_yaml_files_1():

    global b
    b.save_entities_to_yaml_files('/tmp')

    pitz.Bag().load_entities_from_yaml_files('/tmp')
    
def test_append_1():

    b = pitz.Bag()
    b.append(pitz.Task(title='blah', status='irrelevant'))
    
def test_values():

    b = pitz.Bag()

    b.append(pitz.Task(title='blah', difficulty='easy',
        status='unstarted'))

    b.append(pitz.Task(title='blah', difficulty='hard',
        status='unstarted'))

    v = b.values('difficulty')
    assert len(v) == 2
    assert ('easy', 1) in v
    assert ('hard', 1) in v

