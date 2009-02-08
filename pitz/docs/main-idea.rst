+++++++++++++
The main idea
+++++++++++++

I really like `Ditz`_.  There's a few tiny changes I want to make, so
I'm making a python implementation, called **pitz**.

.. _Ditz: http://ditz.rubyforge.org


Features
========

See the `Use cases`_ section for details on all the planned features,
but here's the big picture:

* command-line interface.
* use source control platform to track revisions over time.
* objects serialize and deserialize to some plain-text format, so
  that standard diff tools can expose how issues evolved over time and
  things can be edited with any editor.
* Make it easy to do interesting queries (this is my main beef with ditz
  -- elaborate querying is a headache).
* Let every issue render itself to HTML for both a singular view (one
  thing per page, with links to related things) and a plural view (all
  things in a certain relation, with links to singular view for each).

.. _`Use cases`: use-cases.html


Relations
=========

Tasks, milestones, people, and a bunch of other things are all
relations.

You can make your own relations too.

Any relation supports a singular and a plural command.  Running `pitz
milestones` is sort of like this statement::

    select name, description from milestone;

And running `pitz milestone feb09` is sort of like::

    select * from milestone where name = 'feb09';

Anatomy
=======

First we have a project.yaml.  This thing defines the schema.  In other
words, it specifies that a project might have these relations:

* tasks
* milestones

Then for each relation, the project.yaml specifies what attributes are
in each relation.  For example, one project might have these attributes
on the Task relation:

* name
* description
* createddate

Every relation must have a name and description and name must be
unique in that relation.
