+++++++++
Use cases
+++++++++

These are all the things I want pitz to be able to do.  I'm not hung up
on the exact syntax. I'm just making it up as I go along

Example queries
===============

List all tasks in the system::

    $ pitz tasks

List tasks assigned to me::

    $ pitz tasks assigned-to:matt

List all milestones::

    $ pitz milestones

List all tasks in the milestone named feb09::

    $ pitz tasks milestone:feb09

List just my tasks in the feb09 milestone::

    $ pitz tasks milestone:feb09 assigned-to:matt

List any task assigned to me or Tim::

    $ pitz tasks --assigned-to:[matt,tim]

See a particular milestone in detail (otice how milestone is singular in
this command)::

    $ pitz milestone feb09

See all the attributes on tasks::

    $ pitz attributes task

Example commands
================

Add a new task::

    $ pitz new task

Add a new milestone::

    $ pitz new milestone

Update a particular task::

    $ pitz update task99

Delete one particular task::

    $ pitz delete task99

Comment on a task::

    $ pitz comment task100
