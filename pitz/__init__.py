# vim: set ts=4 sw=4 filetype=python:

"""
Stuff that is useful in lots of different places goes in here.

Stuff that is REALLY useful should be in the awesome clepy package,
which is a grab bag of fanciness.
"""

import logging
import os
import subprocess

__version__ = "1.0.6"

log = logging.getLogger('pitz')


def setup_logging(level=logging.INFO):
    log = logging.getLogger('pitz')

    log.setLevel(level)

    h = logging.StreamHandler()
    h.setLevel(level)

    f = logging.Formatter("%(levelname)s %(name)s: %(message)s")
    h.setFormatter(f)

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

    if 'reverse' in kwargs:
        f.__doc__ = '%s (reversed)' % list(whatever)
    else:
        f.__doc__ = str(list(whatever))

    f.func_name = func_name

    return f


# TODO: Figure out if I should use functools.partial instead.
by_spiciness = by_whatever('by_spiciness', 'peppers')
by_created_time = by_whatever('by_created_time', 'created_time')

by_descending_created_time = by_whatever('by descending created time',
    'created_time', reverse=True)

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
    'milestone', 'status', 'pscore', 'created time', reverse=True)

by_milestone_status_pscore = by_milestone_status_pscore_created_time


class PitzException(Exception):
    """
    All pitz exceptions subclass this guy.
    """


class NoProject(PitzException):
    """
    Indicates that this object can't do what you are asking it to do
    because it doesn't have a pitz.project.Project instance to work
    with.
    """


class ProjectNotFound(PitzException):
    """
    Could not find a project.
    """

class OtherTaskStarted(PitzException):
    """
    Happens when you start a second task while another one is already
    started.
    """

def build_filter(args):
    """
    Return a dictionary suitable for filtering.

    >>> build_filter(['a=1', 'b=2', 'c=[3,4,5]'])
    {'a': '1', 'c': ['3', '4', '5'], 'b': '2'}

    """

    d = dict()
    for a in args:
        attr, value = a.split('=')

        # Make a list of values if we got a string like "[1, 2, 3]"
        if value.startswith('[') and value.endswith(']'):
            value = value.strip('[]').split(',')

        d[attr] = value

    return d


def run_hook(pitzdir, hookscript):

    """
    Run pitzdir/hooks/hookscript, passing in the pitzdir as $1.
    """

    try:
        subprocess.call(
            [os.path.join(pitzdir, 'hooks', hookscript), pitzdir])

    except OSError, ex:
        log.debug(ex)


colors = {

    # regular (darker) colors
    'dark_gray': '\033[0;30m',
    'dark_red': '\033[0;31m',
    'dark_green': '\033[0;32m',
    'dark_yellow': '\033[0;33m',
    'dark_blue': '\033[0;34m',
    'dark_magenta': '\033[0;35m',
    'dark_cyan': '\033[0;36m',
    'dark_gray': '\033[0;37m',
    'dark_crimson': '\033[0;38m',

    # brighter (bolded) colors
    'gray': '\033[1;30m',
    'red': '\033[1;31m',
    'green': '\033[1;32m',
    'yellow': '\033[1;33m',
    'blue': '\033[1;34m',
    'magenta': '\033[1;35m',
    'cyan': '\033[1;36m',
    'white': '\033[1;37m',
    'crimson': '\033[1;38m',

    # text on colored background
    'red_highlight': '\033[1;41m',
    'green_highlight': '\033[1;42m',
    'yellow_highlight': '\033[1;43m',
    'blue_highlight': '\033[1;44m',
    'magenta_highlight': '\033[1;45m',
    'cyan_highlight': '\033[1;46m',
    'gray_highlight': '\033[1;47m',
    'crimson_highlight': '\033[1;48m',

    # miscellaneous other
    'underscore': '\033[0;04m',
    'inverse': '\033[0;07m',
    'concealed': '\033[0;08m',

    # remove color formatting
    'clear': '\033[0m',
}
