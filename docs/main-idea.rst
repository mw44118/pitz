+++++++++++++
The main idea
+++++++++++++

I really like `Ditz`_.  There's a few tiny changes I want to make, so
I'm making a python project, called **pitz**.

.. _Ditz: http://ditz.rubyforge.org

What is pitz
============

Pitz is a issue-tracking system with these goals:

*   Your to-do list lives in flat files right next to your code.

*   The to-do list objects (entities) serialize and deserialize to a
    plain-text format, so that standard diff tools can expose how issues
    evolved over time and objects can be edited with any editor.

*   You can use your source control system (git, svn, zipped files,
    whatever) to track history.

*   Entities can hold arbitrary attributes and values.  In other words,
    the user of the library defines what fields to track.

*   Complex queries are straightforward to write.

Ingredients
===========

*   Pitz uses `yaml`_ to serialize and unserialize data.
*   Pitz uses `IPython`_ for the pitz-shell component and `jinja2`_ to
    produce some output.

.. _yaml: http://yaml.org
.. _IPython: http://ipython.scipy.org
.. _jinja2: http://jinja.pocoo.org/2/
