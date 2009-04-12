# vim: set ts=4 sw=4 filetype=python:

def by_whatever(func_name, *whatever):
    """
    Returns a function suitable for sorting, using whatever.

    >>> e1, e2 = {'a':1, 'b':1, 'c':2}, {'a':2, 'b':2, 'c':1}
    >>> by_whatever('xxx', 'a')(e1, e2)
    -1
    >>> by_whatever('xxx', 'c', 'a')(e1, e2)
    1
    """

    def f(e1, e2):

        return cmp(
            [e1.get(w) for w in whatever],
            [e2.get(w) for w in whatever])

    f.__doc__ = "by_whatever(%s)" % list(whatever)
    f.func_name = func_name
        
    return f

by_spiciness = by_whatever('by_spiciness', 'peppers')
by_created_time = by_whatever('by_created_time', 'created_time')

by_type_status_created_time = by_whatever('by_type_status_created_time', 
    'type', 'status', 'created time')
