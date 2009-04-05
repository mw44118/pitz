# vim: set expandtab ts=4 sw=4 filetype=python:

from datetime import datetime
import yaml

import pitz

from nose.tools import raises
from nose import SkipTest

b = pitz.Bag()

tasks = [
    pitz.Task(b, title='Clean cat box!', creator='Matt'),
    pitz.Task(b, title='Shovel driveway', creator='Matt'),
]


def test_new_bag():

    global tasks
    t1, t2 = tasks

    b = pitz.Bag(entities=tasks)

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

    b = pitz.Bag()

    t = pitz.Task(b, title='Clean cat box!', 
        creator='Matt',
        description='It is gross!')

    assert t.name == t['name']

@raises(ValueError)
def test_must_get_required_attributes():
    
    b = pitz.Bag()
    pitz.Task(b)

def test_as_eav_tuples():

    global tasks
    t1, t2 = tasks
    assert isinstance(t1.as_eav_tuples, list)

    print t1.as_eav_tuples

    assert len(t1.as_eav_tuples) == 5, \
    "got %d tuples back!" % len(t1.as_eav_tuples)

def test_summarized_view():

    global tasks
    t1, t2 = tasks
    assert isinstance(t1.summarized_view, str)
    assert t1.data['title'] in t1.summarized_view

    print(str(t1))

def test_name_must_be_unique():

    raise SkipTest

def test_update_task_status():

    global tasks
    t1, t2 = tasks

    t1['status'] = 'unstarted'
    t1['status'] = 'finished'


def test_comment_on_task():

    global tasks
    t1, t2 = tasks

    t1.comment(
        pitz.Person(title="Matt"),
        datetime.now(),
        "This is a bogus comment")


def test_view_tasks_for_matt():

    p = pitz.Project("Matt's stuff")
    matt = pitz.Person(p, title='Matt')

    t = pitz.Task(p, title='Clean cat box', owner=matt)

    tasks_for_matt = p(type='task', owner=matt)
    assert t in tasks_for_matt

    
def test_view_tasks_for_matt_and_in_next_milestone():

    p = pitz.Project("Matt's stuff")
    matt = pitz.Person(p, title='Matt')
    m = pitz.Milestone(p, title='Next Milestone')

    t = pitz.Task(p, title='Clean cat box', owner=matt, milestone=m)

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

    b = pitz.Bag()

    fp = t1.to_yaml_file('/home/matt/projects/pitz/pitz/junkyard')
    pitz.Entity.from_yaml_file(fp, b)


def test_to_html():
    raise SkipTest

def test_repr():
    
    global tasks
    t1, t2 = tasks

    repr(t1)

