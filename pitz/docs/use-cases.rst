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

    $ pitz tasks --assigned-to matt

List all milestones::

    $ pitz milestones

List all tasks in the milestone named feb09::

    $ pitz tasks --milestone feb09

List just my tasks in the feb09 milestone::

    $ pitz tasks --milestone feb09 --assigned-to matt

By default, every filter is combined with an AND clause.  Here's how to
get any task in milestone feb09 or assigned to me::

    $ pitz tasks --or --milestone feb09 --assigned-to matt

If you need to run a query like::

    (OR

        (AND assigned-to-matt milestone-feb09)
        (AND assigned-to-tim milestone-feb09))

Then first of all, you're crazy.  Write a function and name it foo and
then call it like this::

    $ pitz special foo

Then your function will be called the parameters off the command line
and a parameter that lets you access the data model.

List any task assigned to me or Tim::

    $ pitz tasks --assigned-to matt,tim

See a particular milestone in detail (otice how milestone is singular in
this command)::

    $ pitz milestone feb09

See all the attributes on tasks::

    $ pitz attributes task

Example commands
================

Add a new task::

    $ pitz add task

Add a new milestone::

    $ pitz add milestone

Update a particular task::

    $ pitz update task feb09

Delete one particular task::

    $ pitz delete task task99
