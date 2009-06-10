+++++++++++++
The main idea
+++++++++++++

I really like `Ditz`_.  There's a few tiny changes I want to make, so
I'm making a python project, called **pitz**.

.. _Ditz: http://ditz.rubyforge.org

What is pitz
============

Pitz is a issue-tracking system, with these goals:

* Your to-do list lives right next to the code in your source control.

* The to-do list objects serialize and deserialize to a plain-text
  format, so that standard diff tools can expose how issues evolved over
  time and objects can be edited with any editor.

* Use your source control system (git, svn, zipped files, whatever) to
  track history.

* Allow interesting queries like:

    * Show all the tasks assigned to Matt and linked to milestone 2.0;
    * Show all the milestones with release dates in 2008 or 2009.

* Offer a data model optimized for flexibility so you can add arbitrary
  attributes to issues.

Ingredients
===========

* Pitz uses yaml to serialize and unserialize data.

* All queries can be thought of lists of attribute-value pairs.  Here is
  how to ask for all milestones with release dates in 2008 or 2009::

    >>> p.milestones(type='milestone', 
    ...              release_date=[2008, 2009]) # doctest: +SKIP

  By the way, the p variable is like your handle to the database of
  everything that pitz knows about.

  All the pairs are joined by AND statements.  Using a list in the value
  spot means you accept any value in that list.
