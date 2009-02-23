# vim: set expandtab ts=4 sw=4 filetype=python:

import pitz
from pitz.tests import tasks

from nose.tools import raises
from nose import SkipTest

def test_simplest_query_1():
    """
    Verify we can look up an entity by entity value.
    """

    t1, t2 = tasks
    assert t1.match([('name', 'task-1')])
    assert not t2.match([('name', 'task-1')])

def test_bag_1():
    """
    Verify the bag can find all the comments.
    """
    b = pitz.Bag(tasks)

    found_tasks = b.matching_pairs([('type', 'task')])

    assert len(found_tasks) == 2

    c1, c2 = found_tasks
    assert c1['type'] == 'task'
    assert c2['type'] == 'task'

def test_show_task():
    """
    Verify that we show related information.
    """

    t1, t2 = tasks

    bag = pitz.Bag(tasks)

    singular_view = t1.singular_view(bag)

    print
    print(singular_view)


def test_new_task():
    """
    Verify we can make a new task.
    """

    pitz.Task({'name':'task-1', 'title':'Clean cat box!', 
        'creator':'person-matt',
        'description':'It is gross!', 'type':'task'}),

@raises(ValueError)
def test_must_get_required_attributes():
    
    pitz.Task({'entity':'task-1'})

def test_as_eav_tuples():

    t1, t2 = tasks
    assert isinstance(t1.as_eav_tuples, list)

    assert len(t1.as_eav_tuples) == 7, \
    "got %d tuples back!" % len(t1.as_eav_tuples)

def test_plural_view():

    t1, t2 = tasks
    assert isinstance(t1.plural_view, str)
    assert t1.data['name'] in t1.plural_view
    assert t1.data['title'] in t1.plural_view

@raises(TypeError)
def test_match_1():

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

def test_to_yaml():
    raise SkipTest

def test_from_yaml():
    raise SkipTest

def test_to_html():
    raise SkipTest
