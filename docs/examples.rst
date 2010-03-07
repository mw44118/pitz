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

Print a very pretty PDF example of a task::

    $ pitz-show abc123 | rst2pdf | lp


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

Comment on a task::

    >>> Comment(entity=t, who_said_it="matt',
    ...         title='blah blah',
    ...         text='Blah, blah, blah...') # doctest: +SKIP


More advanced stuff
===================

You can embed an image in a task's description.  Just use regular
restructured text markup, like::

    ..  image:: /home/matt/checkouts/pitz/pitzdir/attached_files/DC00212.jpg
        :alt: picture of me

Right now, you have to use the absolute path to the image file.  I'm
looking for a way to pass in the pitzdir in as a variable.

