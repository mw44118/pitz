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


def test_simplest_query_1():
    """
    Verify we can look up an entity by entity value.
    """

    global tasks

    t1, t2 = tasks
    assert t1.match([('title', 'Clean cat box!')])
    assert not t2.match([('title', 'Clean cat box!')])

def test_matching_pairs():
    """
    Verify the bag can find all the comments.
    """

    global b, tasks

    found_tasks = b.matching_pairs([('type', 'task')])

    assert len(found_tasks) == 2

    c1, c2 = found_tasks
    assert c1['type'] == 'task'
    assert c2['type'] == 'task'

def test_new_bag():

    global tasks
    t1, t2 = tasks

    b = pitz.Bag(entities=tasks)

    assert b.entities[t1.name] == t1
    assert b.entities[t2.name] == t2


def test_show_task():
    """
    Verify that we show related information.
    """

    global tasks
    t1, t2 = tasks

    print
    print(t1.singular_view)


def test_new_task():
    """
    Verify we can make a new task.
    """

    b = pitz.Bag()

    t = pitz.Task(b, title='Clean cat box!', 
        creator='person-matt',
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

    assert len(t1.as_eav_tuples) == 7, \
    "got %d tuples back!" % len(t1.as_eav_tuples)

def test_plural_view():

    global tasks
    t1, t2 = tasks
    assert isinstance(t1.plural_view, str)
    assert t1.data['title'] in t1.plural_view

    print(str(t1))

@raises(TypeError)
def test_match_1():

    global tasks
    t1, t2 = tasks

    t1.match([('owners', 
        ['person-matt', 'person-tim'])])
    
def test_name_must_be_unique():

    raise SkipTest

def test_group_tasks_into_milestones():
    """
    Verify we can put numerous tasks into milestones.
    """

    raise SkipTest

def test_update_task_status():
    raise SkipTest

def test_comment_on_task():
    raise SkipTest

def test_view_tasks_for_matt():
    raise SkipTest
    
def test_view_tasks_for_matt_and_in_next_milestone():
    raise SkipTest

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

