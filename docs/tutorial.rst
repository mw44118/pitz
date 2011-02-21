+++++++++++++++
Getting started
+++++++++++++++

The goal here is for me to walk you through how to start using pitz.

Set up a project
================

Pretend that I'm starting work on a project named frotz::

    $ mkdir frotz && cd frotz

Run this command (added to your path when you ran easy_install
pitz)::

    $ pitz-setup

You'll get asked lots of questions, and at the end, get dumped back out
to the command line, and a fancy new pitzdir directory will hold your
stuff.

Tell your source control system to ignore some files
====================================================

You should **not** track changes in these particular files.  They do
stuff like cache data for quicker retrieval, protect against multiple
processes working simultaneously on the same data, and tell pitz who you
are.

*   project.pickle
*   pitz.pid

me.yaml
-------

The me.yaml file can be tracked as long as you know you're the only one on the
project.  If many people have checkouts, each person's me.yaml file
should be different, so you should not track changes to it.

git example
-----------

I always add these lines to my .gitignore file::

    pitzdir/project.pickle
    pitzdir/pitz.pid
    pitzdir/me.yaml


Create a task
=============

Use pitz-add-task like this::

    $ pitz-add-task

You'll get asked for a title, a description, a milestone, an estimate,
and for components.

You can hit::

    $ pitz-add-task --help

To see options.

See your to-do list
===================

Use pitz-todo::

    $ pitz-todo
    /==================
    frotz: stuff to do
    ==================

    (1 tasks)

    Wash dishes                                                 64ff76
    no owner | unstarted | not estimated | unscheduled | 0
    no tags
    Scrub scrub scrub scrub


Notice that **64ff76** -- that's the first six letters of your task's
UUID, which is a universally unique identifier.  I call it "the frag"
and you can use a frag to identify an entity.

See detail on a single task
===========================

Use the entity's frag to see all the details::

    $ pitz-show 64ff76
    Wash dishes
    ===========

    no owner | unstarted | not estimated | unscheduled

    Description
    -----------
    Scrub scrub scrub scrub

    Attributes
    ----------
    pscore            : 0
    modified_time     : 2009-10-28 16:53:56.206102
    created_time      : 2009-10-28 16:53:52.118334
    frag              : 64ff76
    owner             : 59a06b: no owner
    type              : task
    yaml_file_saved   : 2009-10-28 16:53:56.206466
    uuid              : 64ff7656-d5b7-4f56-b506-714d44d8b3a5

