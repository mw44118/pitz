# vim: set expandtab ts=4 sw=4 filetype=python:

import glob, os
from datetime import datetime
import yaml

import pitz
from pitz.bag import Bag
from pitz.projecttypes.simplepitz import *

from nose.tools import raises
from nose import SkipTest

b = Bag()

tasks = [
    Task(b, title='Clean cat box!', creator='Matt',
        status=Status(title='unstarted')),
    Task(b, title='Shovel driveway', creator='Matt',
        status=Status(title='unstarted')),
]

t1, t2 = tasks

def teardown():
    """
    Delete any files we created.
    """
    for f in glob.glob('/tmp/task-*.yaml'):
        os.unlink(f)


def test_new_bag():

    global t1, t2, tasks

    b = Bag(entities=tasks)

    assert t1 in b
    assert t2 in b


def test_show_task():
    """
    Verify that we show related information.
    """

    global tasks
    t1, t2 = tasks

    print
    print(t1.detailed_view)


def test_new_task():
    """
    Verify we can make a new task.
    """

    b = Bag()

    t = Task(b, title='Clean cat box!', 
        status=Status(title='unstarted'),
        creator='Matt',
        description='It is gross!')

    assert t.uuid == t['uuid']

def test_missing_attributes_replaced_with_defaults():
    """
    Verify we fill in missing attributes with defaults.
    """

    t = Task(title="bogus")
    assert t['status'] == Status(title='unstarted')


def test_summarized_view():

    global tasks
    t1, t2 = tasks
    assert isinstance(t1.summarized_view, str)
    assert t1['title'] in t1.summarized_view


def test_update_task_status():

    global tasks
    t1, t2 = tasks

    t1['status'] = Status(title='unstarted')
    t1['status'] = Status(title='finished')


def test_comment_on_task():

    global b, t1, t2, tasks

    c = Comment(b, who_said_it="matt",
        entity=t1,
        text="blah blah")

    comments_on_t1 = b(type='comment', entity=t1)
    assert len(comments_on_t1) == 1
    assert comments_on_t1[0]['text'] == 'blah blah'


def test_view_tasks_for_matt():

    p = Project("Matt's stuff")
    matt = Person(p, title='Matt')

    t = Task(p, title='Clean cat box', owner=matt, status=Status(title='unstarted'))

    tasks_for_matt = p(type='task', owner=matt)
    assert t in tasks_for_matt

    
def test_view_tasks_for_matt_and_in_next_milestone():

    p = Project("Matt's stuff")
    matt = Person(p, title='Matt')
    m = Milestone(p, title='Next Milestone')

    t = Task(p, title='Clean cat box', owner=matt, milestone=m,
        status=Status(title='unstarted'))

    tasks_for_matt_in_next_milestone = p(type='task', owner=matt, 
        milestone=m)

    assert t in tasks_for_matt_in_next_milestone


def test_yaml():

    global tasks
    t1, t2 = tasks

    yaml.load(t1.yaml)

def test_yaml_file():

    global tasks
    t1, t2 = tasks

    b = Bag()

    fp = t1.to_yaml_file('/tmp')
    Entity.from_yaml_file(fp, b)


def test_to_html():
    raise SkipTest

def test_repr():
    
    global tasks
    t1, t2 = tasks

    repr(t1)

