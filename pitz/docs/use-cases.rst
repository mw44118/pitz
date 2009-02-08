+++++++++
Use cases
+++++++++

These are all the things I want pitz to be able to do.  I'm not hung up
on the exact syntax. I'm just making it up as I go along


List all tasks in the system::

    $ pitz tasks

List tasks assigned to me::

    $ pitz --assigned-to matt

List all milestones::

    $ pitz milestones

List all tasks in the milestone named feb09::

    $ pitz tasks --milestone feb09

Now look at just my tasks in the feb09 milestone::

    $ pitz tasks --milestone feb09 --assigned-to matt

Show any task assigned to me or Tim::

    $ pitz tasks --assigned-to matt,tim




