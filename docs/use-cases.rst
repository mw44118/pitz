++++++++++++
Example uses
++++++++++++

Examples from command-line
==========================

List all tasks in the system::

    $ pitz-everything

List tasks assigned to me::

    $ pitz-everything type=task assigned-to=matt

List all milestones::

    $ pitz-everything type=milestone

List all tasks in the milestone named feb09::

    $ pitz-everything type=task milestone=feb09

List just my tasks in the feb09 milestone::

    $ pitz-everything type=task milestone=feb09 assigned-to=matt

List any task assigned to me or Tim::

    $ pitz-everything type=task assigned-to=[matt,tim]

See a particular milestone in detail::

    # first get a list of all milestones.
    $ pitz-everything type=milestone
    $ pitz-show asdf12 # asdf12 is a UUID fragment.

See all the attributes on tasks::

    $ pitz-show hjkl98 # hjkl98 is a UUID fragment.

Examples from within pitz-shell
===============================

Add a new task::

    $ pitz-shell
    >>> p.append(Task(...)) # doctest: +SKIP

Add a new milestone::

    >>> p.append(Milestone(...)) # doctest: +SKIP

Link a task to a milestone::

    >>> m1 = p.milestones[0] # doctest: +SKIP

    >>> # you can use UUID fragments to get things
    >>> t = p['hjkl98'] # doctest: +SKIP 
    >>> t['milestone'] = m1 # doctest: +SKIP

Comment on a task t::

    >>> Comment(entity=t, who_said_it="matt', 
    ...         title='blah blah',
    ...         text='Blah, blah, blah...') # doctest: +SKIP
