+++++++++++++
Pitz Tutorial
+++++++++++++

The goal here is for me to walk you through how to start using pitz.

Install pitz
============

Use a virtualenv or just install pitz as root like this::

    $ sudo easy_install pitz


Set up a project to use pitz
============================

Typically I use stuff like virtualenv and paster, but for this tutorial,
I'll keep things simple.  Pretend that I'm starting work on a project
named frotz::

    $ mkdir frotz && cd frotz

Run this command (added to your path when you ran easy_install
pitz)::

    $ pitz-setup
    I need to make a directory named 'pitzfiles'.  Where should I put it?
    The default place is right here (.).
       0. pitz.projecttypes.simplepitz: Simple: milestones and tasks.

       1. pitz.projecttypes.agilepitz: Agile: releases, iterations, stories,
    tasks, and velocity.

    Choose one.0
    All done!  Run pitz-shell
    /home/matt/frotz/pitzfiles/simpleproject-c97241b5-be69-4ab4-ba86-3609cf3537e5.yaml
    to start working...

Now that created a pitzfiles directory with a single file in there::

    $ ls
    pitzfiles

    $ ls pitzfiles/
    simpleproject-c97241b5-be69-4ab4-ba86-3609cf3537e5.yaml


Start using pitz
================

Right now, the only finished way to use pitz is from within a python
session like this::

    $ pitz-shell pitzfiles/simpleproject-c97241b5-be69-4ab4-ba86-3609cf3537e5.yaml 

This will fire up a python shell, load a bunch of pitz classes,  and
create a variable called p.  p is an instance of the class you picked
out during setup.  All the tasks, milestones, people, comments, etc for
the frotz project are all linked to p::

    >>> p
    <pitz.SimpleProject '' (empty) sorted by by_whatever(['created_time'])>


Create a task
=============

Now I'll create a task for my frotz project by instantiating the Task class::

    >>> t = Task(title="Write a setup.py file for frotz")

Link this new task to the project like this::

    >>> p.append(t)


Edit the task
=============

Now look at the to-do list for the project::

    >>> p.todo
    <pitz.Bag 'Stuff to do' (1 task entities) sorted by by_whatever(['created_time'])>

The repr view just summarizes stuff.  Print the project to get more detail::

    >>> print(p.todo)
    ===========
    Stuff to do
    ===========

    (1 task entities)
    -----------------

       0: 0e6fcc Write a setup.py file for frotz (unstarted)
