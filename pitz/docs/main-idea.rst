+++++++++++++
The main idea
+++++++++++++

I really like `Ditz`_.  There's a few tiny changes I want to make, so
I'm making a python implementation, called **pitz**.

.. _Ditz: http://ditz.rubyforge.org

What is pitz
============

Pitz is (going to be) yet another bugtracking system, with these goals:

* Your to-do list lives right next to the code in your source control.

* The to-do list objects serialize and deserialize to a plain-text
  format, so that standard diff tools can expose how issues evolved over
  time and objects can be edited with any editor.

* Use your source control system (git, svn, zipped files, whatever) to
  track history.

* Using a really simple syntax, allow interesting queries like:

    * Show all the tasks assigned to Matt and linked to milestone 2.0;
    * Show all the milestones with release dates in 2008 or 2009.

* Every issue can render itself to HTML for both a singular view (one
  thing per page, with links to related things) and a plural view (all
  things in a certain relation, with links to singular view for each).

* Offer a data model optimized for flexibility so you can add arbitrary
  attributes to issues.

Ingredients
===========

* Use yaml to serialize and unserialize data.  Instead of storing
  everything in one big file, spread stuff out across lots and lots of
  files.  This will make tracking revisions with whatever SCM you use
  much easier.

* All queries can be thought of lists of attribute-value pairs.  Here is
  how to ask for all milestones with release dates in 2008 or 2009::

    >>> p.milestones(type='milestone', 
    ...              release_date=[2008, 2009]) # doctest: +SKIP

  By the way, every pitz install creates a variable p.  The p variable
  is like your handle to the database of everything.

  All the pairs are joined by AND statements.  Using a list in the value
  spot means you accept any value in that list.
