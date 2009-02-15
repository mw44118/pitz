# vim: set expandtab ts=4 sw=4 filetype=python:

from pprint import pprint

import pitz

tasks = [
    pitz.Entity({'entity':'task-1', 'title':'Clean cat box!'}),
    pitz.Entity({'entity':'task-2', 'title':'Shovel driveway'}),
]

def test_simplest_query_1():
    """
    Verify we can look up an entity by entity value.
    """

    t1, t2 = tasks
    assert t1.match([('entity', 'task-1')])
    assert not t2.match([('entity', 'task-1')])
