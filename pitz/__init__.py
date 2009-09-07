# vim: set ts=4 sw=4 filetype=python:

"""
Stuff that is useful in lots of different places goes in here.

Stuff that is really REALLY useful should be in the awesome clepy
package, which is a grab bag of fanciness.
"""

from __future__ import with_statement

import logging, os, subprocess, tempfile
from pitz.exceptions import *

__version__ = "0.3"


# This bugs me.  I don't like how instead of just defining stuff, I'm
# making stuff really happen.
log = logging.getLogger('pitz')
log.setLevel(logging.DEBUG)

h = logging.StreamHandler()
log.addHandler(h)

# TODO: Move this into the clepy package.
def by_whatever(func_name, *whatever, **kwargs):
    """
    Returns a function suitable for sorting, using whatever.

    >>> e1, e2 = {'a':1, 'b':1, 'c':2}, {'a':2, 'b':2, 'c':1}
    >>> by_whatever('xxx', 'a')(e1, e2)
    -1
    >>> by_whatever('xxx', 'c', 'a')(e1, e2)
    1
    >>> by_whatever('xxx', 'c', 'a', reverse=True)(e1, e2)
    -1

    """

    def f(e1, e2):

        y = cmp(
            [e1.get(w) for w in whatever],
            [e2.get(w) for w in whatever])

        if kwargs.get('reverse'):
            y *= -1
            
        return y

    f.__doc__ = "by_whatever(%s)" % list(whatever)
    f.func_name = func_name
        
    return f


# TODO: Figure out if I should use functools.partial instead.
by_spiciness = by_whatever('by_spiciness', 'peppers')
by_created_time = by_whatever('by_created_time', 'created_time')

by_type_status_created_time = by_whatever('by_type_status_created_time',
    'type', 'status', 'created time')

by_milestone = by_whatever('by_milestone',
    'milestone', 'type', 'status', 'created time')

def by_pscore_and_milestone(e1, e2):

    y = cmp(e1['pscore'], e2['pscore']) * -1
    if y != 0:
        return y

    else:
        return by_milestone(e1, e2)


def by_status(e1, e2):
    """
    Compare the status attribute of the two entities.
    """

    y = -1 * cmp(e1['status'], e2['status'])

    if y != 0:
        return y

    else:
        return by_created_time(e1, e2)


by_milestone_status_pscore_created_time = by_whatever(
    'by_milestone_status_pscore_created_time',
    'milestone', 'status', 'pscore', 'created time')

by_milestone_status_pscore = by_milestone_status_pscore_created_time

