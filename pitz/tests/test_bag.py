# vim: set expandtab ts=4 sw=4 filetype=python:

import pitz
import pitz.entity
from pitz.junkyard import Task
from pitz.bag import Bag

from nose.tools import raises
from nose import SkipTest

b = Bag("Testing bag")

tasks = [

    Task(b, title='Clean cat box!', creator='person-matt',
        status='really important'),

    Task(b, title='Shovel driveway', creator='person-matt',
        status='not very important'),
]

def test_matches_dict():

    global b, tasks
    b.matches_dict(type='task')

def test_new_bag():

    global tasks
    t1, t2 = tasks

    b2 = Bag(entities=tasks)

    assert t1 in b2
    assert t2 in b2

    b.order()
    
def test_append_1():

    b = Bag()
    b.append(pitz.entity.Entity(title='blah', status='irrelevant'))
    
def test_values():

    b = Bag()

    b.append(pitz.entity.Entity(title='blah', difficulty='easy',
        status='unstarted'))

    b.append(pitz.entity.Entity(title='blah', difficulty='hard',
        status='unstarted'))

    v = b.values('difficulty')
    assert len(v) == 2
    assert ('easy', 1) in v
    assert ('hard', 1) in v

