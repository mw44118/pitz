+++++++++++++
The main idea
+++++++++++++

I really like `Ditz`_.  There's a few tiny changes I want to make, so
I'm making a python implementation, called **pitz**.

.. _Ditz: http://ditz.rubyforge.org

Features
========

* Your to-do list lives right next to the code in your source control.

* command-line interface.

* Use your source control system to track revisions over time.

* The to-do list objects serialize and deserialize to some plain-text
  format, so that standard diff tools can expose how issues evolved over
  time and objects can be edited with any editor.

* Interesting queries are straightforward.  This is my main beef with
  ditz -- I find it difficult to get information like all tickets in the
  next release that have a certain status.

* Let every issue render itself to HTML for both a singular view (one
  thing per page, with links to related things) and a plural view (all
  things in a certain relation, with links to singular view for each).

* Prioritize flexibility over performance in the data model.
