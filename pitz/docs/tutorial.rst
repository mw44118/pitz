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

Right now, the best way to use pitz is from within a python
session like this::

    $ pitz-shell

This will fire up IPython, load a bunch of pitz classes,  and create a
variable called p.  p is an instance of the class you picked out during
setup.  All the tasks, milestones, people, comments, etc for the frotz
project are all linked to p::

    In [1]: p

    Out[1]: <pitz.SimpleProject 'Pitz' (63 task entities, 3 comment entities, 2 person entities, 2 milestone entities) sorted by by_whatever(['type', 'status', 'created time'])>


Create a task
=============

Now I'll create a task for my frotz project by instantiating the Task class::

    In [2]: t = Task(title="Wash dishes")

Link this new task to the project like this::

    In [3]: p.append(t)

Edit the task
=============

Now look at the to-do list for the project::

    In [4]: p.todo

    Out[4]: <pitz.Bag 'Pitz: stuff to do' (29 task entities) sorted by by_whatever(['type', 'status', 'created time'])> 

The repr view just summarizes stuff.  Print the project to get more detail::

    In [5]: print(p.todo)
    =================
    Pitz: stuff to do
    =================

    (29 task entities)
    ------------------

       0: c35df2 Demonstrate really simple tasks and priorities workflow (started)
       1: 004821 replace pointers dictionary with simpler UUID attribute detection (unstarted)
       2: aa9b97 Update entities by loading a CSV file (unstarted)
       3: d00cfb Support intersection, union, and other set operations on bags (unstarted)
       4: d904ab Add a property on the project to list recently updated stuff (unstarted)
       5: e1350e Make a pitz-add script (unstarted)
       6: 43a2b0 Write a pitz-edit script (unstarted)
       7: 64efab Make an HTML view of project (unstarted)
       8: b442e8 Support hooks (unstarted)
       9: 1ddfbe Make a better detailed view for tasks (unstarted)
      10: b78791 Allow summarized vs detailed view to be configurable (unstarted)
      11: c0af8c Write script to show and update entity statuses (unstarted)
      12: a6d153 Add a proper Component class to simplepitz. (unstarted)
      13: f592f3 Make some web view that allows tasks to be dragged around (unstarted)
      14: 28d79d Allow people to attach files to entities (unstarted)
      15: 056ab2 Write a function that lists values for an attribute and also offers a chance to input a new value (unstarted)
      16: 6484b9 Load new entities from a CSV file (unstarted)
      17: ed08ef Start up a pager when scripts exceed terminal height (unstarted)
      18: 14aeac Alter detailed view to show information like related milestones, components, comments, etc. (unstarted)
      19: 4ca9f1 write data to yaml in order (unstarted)
      20: 6b02c8 Support using substring of uuid as lookup (unstarted)
      21: 68b776 Write a pitz-edit script (unstarted)
      22: 7dea57 Somehow indicate when an entity has pointers to it (unstarted)
      23: f70307 explore paster and see if it makes sense to make pitz use paster (unstarted)
      24: 9e13f8 Copy pitz project file to allow local edits (unstarted)
      25: 985141 Write documentation to show how and why to edit Bag and Entity subclasses (unstarted)
      26: 1e583c Write a pitz-add script (unstarted)
      27: 84b97e Demonstrate ditz workflow with pitz (unstarted)
      28: 7fc15f Wash dishes (unstarted)
