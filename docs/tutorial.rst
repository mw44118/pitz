+++++++++++++++++++++++
How to start using pitz
+++++++++++++++++++++++

The goal here is for me to walk you through how to start using pitz.

Install pitz
============

Use a virtualenv or just install pitz as root like this::

    $ sudo easy_install pitz

Set up a project to use pitz
============================

Pretend that I'm starting work on a project named frotz::

    $ mkdir frotz && cd frotz

Run this command (added to your path when you ran easy_install
pitz)::

    $ pitz-setup

The pitz-setup script will ask a few questions.  Here's the first one::

    I need to make a directory named 'pitzfiles'.  Where should I put it?
    The default place is right here (.)

I suggest putting the pitzdir at the very top of your project, in the
same directory as your setup.py file (if one exists).

The next question is asking you about what kind of pitz-project you want
to set up.  Here's your choices::

    0. pitz.projecttypes.simplepitz: Simple: milestones and tasks.

    1. pitz.projecttypes.agilepitz: Agile: releases, iterations, stories,
    tasks, and velocity.

    Choose one.

I'll choose the simple project.  Now the script tells
what to do next::

    All done!  Run pitz-shell [path to project file] to start.

Now that created a pitzfiles directory with a single file in there::

    $ ls
    pitzdir

    $ ls pitzdir/
    simpleproject-c97241b5-be69-4ab4-ba86-3609cf3537e5.yaml


Start using pitz
================

I'll run pitz-everything to see, well, everything in my pitzdir::

    $ pitz-everything

    =====
    frotz
    =====

    (empty)
    -------

We haven't made any tasks yet.  Right now, the best way to insert or edit stuff
is from within a python session.  You can start one like like this::

    $ pitz-shell

This will fire up IPython, load a bunch of pitz classes,  and create a
variable called p.  p is an instance of the class you picked out during
setup.  All the tasks, milestones, people, comments, etc for the frotz
project are all attributes on p.  Consider p something like your
connection to the database.

Or if that bugs you, consider it just a big list.


Create a task
=============

Now I'll create a task for my frotz project by instantiating the Task class::

    In [1]: t = Task(title="Wash dishes")

    In [2]: p.append(t)

    In [3]: print(p)
    =====
    frotz
    =====

    (1 task entities)
    -----------------

    0: c2b023 Wash dishes (unstarted)

I usually make a task and append it all in one line like this::

    In [4]: p.append(Task(title="Take out garbage"))

    In [5]: print(p)
    =====
    frotz
    =====

    (2 task entities)
    -----------------

    0: c2b023 Wash dishes (unstarted)
    1: 280232 Take out garbage (unstarted)

Hit ctrl-d to close the session.  You'll be asked if you want to save
your work::

    In [6]: 
    Do you really want to exit ([y]/n)? 
    Write out updated yaml files? ([y]/n) 

Now you can rerun pitz-everything and see our new issues::

    $ pitz-everything
    =====
    frotz
    =====

    (2 task entities)
    -----------------

    0: c2b023 Wash dishes (unstarted)
    1: 280232 Take out garbage (unstarted)

Play with pitz-everything --help to see more options.
