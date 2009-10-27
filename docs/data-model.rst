+++++++++++++++++++
Data Model Overview
+++++++++++++++++++

There are two classes in pitz: entities and bags.  Everything else are
subclasses of these two.

Entities
========

Making them
-----------

Every entity is an object like a dictionary.  You can make an entity
like this::

    >>> from pitz.entity import Entity
    >>> e = Entity(title="example entity",
    ...            creator="Matt",
    ...            importance="not very")

You can also load an entity from a yaml file, but I'll explain that
later.

You can look up a value for any attribute like this::

    >>> e['title']
    'example entity'
    >>> sorted(e.keys()) #doctest: +NORMALIZE_WHITESPACE
    ['attached_files', 'created_time', 'creator', 'description', 'frag',
    'importance', 'modified_time', 'pscore', 'title', 'type', 'uuid']
    >>> e['type']
    'entity'

Viewing them
------------

Entities have a summarized view useful when you want to see a list of
entities, and a detailed view that shows all the boring detail::

    >>> e.summarized_view #doctest: +SKIP
    '86bd21: example entity'

    >>> print(e.detailed_view) #doctest: +SKIP
    example entity (entity)
    -----------------------

    name:
    entity-bdd31951-cff0-42a5-92b4-97ef966a6f6f

    creator:
    Matt

    importance:
    not very

    title:
    example entity

    modified_time:
    2009-04-04 07:47:09.456068

    created_time:
    2009-04-04 07:47:09.456068

    type:
    entity

Notice the attributes I never set, like name, type, created_time, and
modified_time.  The __init__ method of the entity class makes these
automatically.

By the way, you can ignore the #doctest: +SKIP comment.  That is there
so the doctests will skip trying to running this example, which will
generate unpredictable values.

Saving and loading them
-----------------------

Entities have an instance method named to_yaml_file and a from_yaml_file
classmethod.  Here's how to use them::

    >>> outfile = e.to_yaml_file('.') # Writes file to this directory.
    >>> e2 = Entity.from_yaml_file(outfile)


Bags
====

Making them
-----------

While entities are based on dictionaries, bags are based on lists.  You
can give a bag instance a title, which is nice for remembering what it
is you want it for.  Bags make it easy to organize a bunch of entities::

    >>> from pitz.bag import Bag
    >>> b = Bag(title="Stuff")
    >>> b.append(e)
    <pitz.Bag 'Stuff' (1 entities)>

Viewing them
------------

Converting a bag to a string prints the summarized view of all the
entities inside::

    >>> print(b) #doctest: +SKIP
    =====
    Stuff
    =====

    1 entities
    -----------------

       0: example entity (entity entities)


That number 0 can be used to pull out the entity at that position, just
like a regular boring old list::

    >>> e == b[0]
    True

Querying them
-------------

Bags have a matches_dict method that accepts a bunch of key-value pairs
and then returns a new bag that contains all the entities in the first
bag that match all those key-value pairs.

First, I'll make a few more entities::

    >>> e1 = Entity(title="example #1", creator="Matt",
    ...             importance="Really important")
    >>> e2 = Entity(title="example #2", creator="Matt",
    ...             importance="not very")

Now I'll make a new bag that has both of these new entities::

    >>> b = Bag('Everything')
    >>> b.append(e1)
    <pitz.Bag 'Everything' (1 entities)>
    >>> b.append(e2)
    <pitz.Bag 'Everything' (2 entities)>
    >>> print(b) #doctest: +SKIP
    Everything
    ==========

    (2 entities)
    -------------------

       0: 5fdcb0: example #1
       1: 407b8d: example #2

Here is how to get a new bag with just the entities that have an
importance attribute set to "not very"::

    >>> not_very_important = b.matches_dict(importance="not very")
    >>> len(not_very_important) == 1
    True
    >>> not_very_important[0] == e2
    True

Since matches_dict is the most common method I call on a bag, I made the
__call__ method on the Bag class run matches_dict.  So that means this
works just as well::

    >>> not_very_important = b(importance="not very")

I wrote a does_not_match_dict method on bags.  Using these together
covers all the weird queries I have needed so far.  For example, here is
how I found all the tasks assigned to me with any status except
'finished'::

    >>> todo_for_matt = b(type='task', assigned_to='Matt')\
    ... .does_not_match_dict(status='finished')

Saving and loading them
-----------------------

Bags can send all contained entities to yaml files with to_yaml_files,
and bags can load a bunch of entities from yaml files with
from_yaml_files.

The Special Project Bag
=======================

After I finished bags and entities, I thought I was done, but then I ran
into a few frustrations:

* When I made a bunch of entities, but didn't append them all into one
  bag, then I couldn't run filters across all of them.

* At the end of a session, it wasn't easy for me to make sure that all
  of the entities got saved out to yaml.

* I couldn't figure out an elegant way to store one entity as a value
  for another entity's attribute.

So I made a "special" Bag subclass called Project.  The idea here is
that every entity should be a member of the project bag.  Also, every
entity should have a reference back to the project.

Using a project is easy.  Just pass it in as the first argument when you
make an entity.  Imagine I want to link some tasks to Matt and some
other tasks to Lindsey.  First I make a project::

    >>> from pitz.bag import Project
    >>> weekend_chores = Project(title="Weekend chores")

Now I make the rest of the entities::

    >>> matt = Entity(weekend_chores, title="Matt")
    >>> lindsey = Entity(weekend_chores, title="Lindsey")
    >>> t1 = Entity(weekend_chores, title="Mow the yard", assigned_to=matt)
    >>> t2 = Entity(weekend_chores, title="Buy some groceries",
    ...             assigned_to=lindsey)


Now it is easy to get tasks for matt::

    >>> chores_for_matt = weekend_chores(assigned_to=matt)
    >>> mow_the_yard = chores_for_matt[0]
    >>> mow_the_yard['assigned_to'] == matt
    True

Pointers
========
    
There's a problem in that last example: when I send this mow_the_yard
entity out to a YAML file, what will I store as the value for the
"assigned_to" attribute?

In SQL, this is what foreign keys are good for.  In my chores table, I
would store a reference to a particular row in the people table.

I wanted the same functionality in pitz, so I came up with pointers.
First I made sure that every entity has a unique name.  The __init__
method of Entity uses uuid from the standard library to make sure that
every entity has an attribute 'uuid' with a unique value.

Next I wrote these two instance methods:

* replace_pointers_with_objects
* replace_objects_with_pointers

This is dry stuff, so here's an example::

    >>> class Chore(Entity):
    ...     pass
    >>> class Person(Entity):
    ...     pass
    >>> matt = Person(weekend_chores, title="Matt")
    >>> lindsey = Person(weekend_chores, title="Lindsey")
    >>> ch1 = Chore(weekend_chores, title="Mow the yard", assigned_to=matt)
    >>> ch2 = Chore(weekend_chores, title="Buy some groceries",
    ...             assigned_to=lindsey)

After running the replace_objects_with_pointers method, ch1 doesn't have a
reference to the matt object.  Instead, it has matt's uuid now::

    >>> isinstance(ch1['assigned_to'], Person)
    True
    >>> ch1 = ch1.replace_objects_with_pointers()
    >>> import uuid
    >>> isinstance(ch1['assigned_to'], uuid.UUID)
    True

Now I can send this data out to a yaml file.  And when I load it back in
from yaml, I can then reverse this action, and go look up an entity with
the same name::

    >>> mu = matt.uuid
    >>> matt == weekend_chores.by_uuid(mu)
    True

In practice, I convert all the entities to pointers, then write out the
yaml files, then convert all the pointers back into objects
automatically.  But converting pointers back into objects requires a
project instance.

Teardown
--------

You can ignore this part.  I just need to clean up some files created in
the doctests.

    >>> import glob, os
    >>> x = [os.unlink(f) for f in glob.glob('entity-*.yaml')]
