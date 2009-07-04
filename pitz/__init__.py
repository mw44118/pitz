# vim: set ts=4 sw=4 filetype=python:

"""
Stuff that is useful in lots of different places goes in here.

Stuff that is really REALLY useful should be in the awesome clepy
package, which is a grab bag of fanciness.
"""

from __future__ import with_statement

import logging, os, subprocess, tempfile
from pitz.exceptions import *

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger('pitz')

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


# TODO: Move this into the clepy package.
def edit_with_editor(s=None):
    """
    Open os.environ['EDITOR'] and load in text s.
    
    Returns the text typed in the editor.
    """

    # This is the first time I've used with!
    with tempfile.NamedTemporaryFile() as t:

        if s:
            t.write(s)
            t.seek(0)

        subprocess.call([os.environ.get('EDITOR', 'vi'), t.name])
        return t.read()
