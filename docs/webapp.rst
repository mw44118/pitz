+++++++++++++++
The pitz webapp
+++++++++++++++

.. contents::

GET URLs
~~~~~~~~

For all classes in the project, you should be able to run at least the
.all() method and the .by_title method.

======================================= ===============================
URL                                     translation
======================================= ===============================
/                                       p()
/?type=task                             p(type='task')
/?type=milestone&reached=0              p(type='milestone', reached=0)
/?owner=matt&owner=lindsey              p(owner=['matt', 'lindsey'])
/?type=activity                         p(type='activity')

/Person/by_title/matt/my_todo           Person.by_title('matt').my_todo
/Tag/all                                Tag.all()

/Task/all?status=unstarted              Tag.all().matches_dict(
                                            status=['unstarted'])

/Task/all/view/detailed                 Task.all().detailed_view
/Person/by_title/matt/my_todo           Person.by_title('matt').my_todo

/Tag/all                                Tag.all()

/?owner=matt&owner=lindsey              p(owner=['matt', 'lindsey'])

======================================= ===============================

POST URLs
~~~~~~~~~

======================================= ===============================
URL                                     translation
======================================= ===============================
/Entity/new                             Insert a new entity using data
                                        in the post body.

/Entity/by_frag/abc123/update           Update some attribute (or
                                        attributes) on this entity.

/Entity/by_frag/abc123/destroy          Tell this entity to destroy
                                        itself.              

======================================= ===============================

Set the format with HTTP_ACCEPT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The code internally works a little like this::

    if 'application/x-pitz in Accept:
        return data formatted with bash colorization

    elif if 'text/html' in Accept or '*/*' in Accept:
        return HTML format of data

    else:
        return text/plain

Filter with QUERY_STRING
~~~~~~~~~~~~~~~~~~~~~~~~

All of the queries below are GET requests.

======================================= ===============================
URL                                     translation
======================================= ===============================
/                                       p()
/?type=task                             p(type='task')
/?type=milestone&reached=0              p(type='milestone', reached=0)
/?owner=matt&owner=lindsey              p(owner=['matt', 'lindsey'])
/?type=activity                         p(type='activity')
======================================= ===============================

Encoding lists of values
~~~~~~~~~~~~~~~~~~~~~~~~

I wrestled with how to represent concepts like "attribute can be this or
that".  I could do it either of these ways:

1.  owner=matt&owner=lindsey
2.  owner=matt,lindsey

I decided to go with #1 because it is obvious that there are two keys
with the same name.  It might be possible that #2 means that I need to
match an attribute that is exactly defined as "matt,lindsey".

In scenario #2, my parsing code would need to treat commas as special
characters.  And then I would need to allow the special commas to be
escaped somehow.

Using wget
~~~~~~~~~~

These examples assume you are running the webapp on localhost, port
8000.  The --quiet option hides lots output that ain't critical and the
-O - option tells wget to write to standard output.

List all tags::

    $ wget -q -O - http://localhost:8000/?type=tag

List all tags and request colorized output::

    $ wget --header="Accept:application/x-pitz" \
    -q -O - http://localhost:8000/?type=tag


Calling methods on classes
~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to get the to-do list for matt, I'd have to use a query string
like::

    ?type=task&owner=matt&status=unstarted&status=started&status=paused

That is pretty nasty.  Meanwhile, in regular python, I can do this::

    Person.by_title('matt').my_todo

It is possible to call **some** methods through the webapp.   The table
below shows a few examples. All of these queries are GET requests.

======================================= ===============================
URL                                     translation
======================================= ===============================
/Person/by_title/matt/my_todo           Person.by_title('matt').my_todo
/Tag/all                                Tag.all()

/Task/all?status=unstarted              Tag.all().matches_dict(
                                            status=['unstarted'])


======================================= ===============================

Set the view
~~~~~~~~~~~~

Bags have just two views (right now).  Entities have lots of
views.

To choose the view you want, put something like this in the URL::

    /Person/by_title/matt/view/detailed

To set the view on a query, do something like this::

    /Task/all/view/detailed?status=unstarted

and that will translates to::

    Task.all().matches_dict(status='unstarted').detailed_view
