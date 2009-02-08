The main idea
=============

I really like `Ditz`_.  There's a few tiny changes I want to make, so
I'm making a python implementation, called **pitz**.

.. _Ditz: http://ditz.rubyforge.org

Blobs
=====

Blobs are really boring.  They're bags of traits.  Every blob needs at
least an ID field, which has to be globally unique across all blobs.

Also, every blob has a type, and running::

    $ pitz types

will print a list of all defined blob types.

The pitz equivalent of a ditz issue is a subclassed blob, maybe with
these traits:

* ID
* type
* title
* description
* milestone
* person working on it
* status

Traits
======

Each trait can be a literal or a pointer.  Pointers are traits that
refer to some other trait container.  Literals are traits where the
value is stored inside this trait container.

Any trait has a name, a value, a blob that it is attached to, and a
type.  For example, in the issue above, there is a trait named status, 
with a value like "finished" or "in progress" or "not started" or
whatever.  The trait is attached to one particular blob, and is a trait
type of "pointer".

Literal traits
==============

The value for a literal trait is stored in the blob.  I'm using literal
in the assembly programming sense of the word, where a register doesn't
hold the memory address of a variable; instead it holds the actual
value.

Pointer traits
==============

Pointers hold references to other blobs.  So when an issue blob has a
pointer trait named milestone, then that trait holds a reference to a
milestone blob.

