# vim: set expandtab ts=4 sw=4 filetype=python:

"""
Stuff in here is for profiling and timing.
"""

import cProfile
import os
import pstats
import timeit

from collections import namedtuple

StatementAndSetup = namedtuple('StatementAndSetup', 'stmt setup')

generic_setup = """
from pitz.project import Project
from pitz.entity import Entity
p = Project(title='odd and even entities',
    entities=[
        Entity(title='entity %d' % i,
            odd_even = ('even', 'odd')[i%2]) for i in xrange(1, 101)])
"""

odd_even_bag = """
from pitz.bag import Bag
from pitz.entity import Entity
b = Bag(title='odd and even entities',
        entities=[Entity(
            title='entity %d' % i,
            odd_even = ('even', 'odd')[i%2]) for i in xrange(1, 101)])
"""

entity_setup = """
from pitz.entity import Entity
e = Entity(title='boring', a=1, b=2, c=3, d=6)
"""

# Map cute name to a tuple of stmt, setup.
commands = {

    'my_todo': StatementAndSetup("""p.me.my_todo""", generic_setup),
    'me': StatementAndSetup("""p.me""", generic_setup),
    'todo': StatementAndSetup("""p.todo""", generic_setup),

    'b.matches_dict': StatementAndSetup(
        """b.matches_dict(odd_even='odd')""", odd_even_bag),

    'b.does_not_match_dict': StatementAndSetup(
        """b.does_not_match_dict(odd_even='odd')""", odd_even_bag),

    'e.matches_dict': StatementAndSetup(
        'e.matches_dict(a=1, b=2, c=3, d=[4,5,6])',
        entity_setup),
}

def prof_this(k):
    stmt, setup = commands[k]
    exec setup
    f = os.path.join('/tmp', '%s.profile' % k)
    cProfile.runctx(stmt, globals(), locals(), filename=f)
    return pstats.Stats(f)

def time_this(k, number=100):
    stmt, setup = commands[k]
    return min(timeit.Timer(stmt, setup).repeat(3, number))
