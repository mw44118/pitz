# vim: set expandtab ts=4 sw=4 filetype=python:

import pitz
from pitz.tests import tasks, people, comments
from nose import SkipTest

def test_simplest_query_1():
    """
    Verify we can look up an entity by entity value.
    """

    t1, t2 = tasks
    assert t1.match([('entity', 'task-1')])
    assert not t2.match([('entity', 'task-1')])

def test_bag_1():
    """
    Verify the bag can find all the comments.
    """

    b = pitz.Bag(tasks + people + comments)

    found_comments = b.matching_pairs([('type', 'comment')])

    assert len(found_comments) == 2

    c1, c2 = found_comments
    assert c1['type'] == 'comment'
    assert c2['type'] == 'comment'

def test_show_task():
    """
    Verify that we show related information.
    """

    t1, t2 = tasks

    bag = pitz.Bag(tasks + people + comments)

    singular_view = t1.singular_view(bag)

    print
    print(singular_view)


def test_new_task():
    """
    Verify we can make a new task.
    """

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
