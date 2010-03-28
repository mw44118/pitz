# vim: set expandtab ts=4 sw=4 filetype=python:

"""
Bags and Bag subclasses.
"""

from __future__ import with_statement

import collections
import csv
import logging
import os
import subprocess
from uuid import UUID, uuid4
from urllib import quote_plus

import clepy
import jinja2
import tempita

import pitz

log = logging.getLogger('pitz.bag')

# Not too happy about this code, but I don't know how to make this work
# python in 2.5 any other way.
if hasattr(collections, 'MutableSequence'):
    BagSuperclass = collections.MutableSequence
else:
    BagSuperclass = object


class Bag(BagSuperclass):
    """
    Bags act like lists with a few extra methods.
    """

    def __init__(
        self, title='', html_filename=None, uuid=None,
        pathname=None, entities=(),
        order_method=pitz.by_pscore_and_milestone,
        jinja_template=None, shell_mode=False, **kwargs):

        self.title = title
        self.pathname = pathname
        self.order_method = order_method
        self._html_filename = html_filename
        self.jinja_template = jinja_template or 'bag.html'
        self._shell_mode = shell_mode

        self._elements = list()

        if uuid:
            self.uuid = uuid

        # Make a unique uuid if we didn't get one.
        if not uuid:
            self.uuid = uuid4()

        # These will get populated in self.append.
        self.entities_by_uuid = dict()
        self.entities_by_frag = dict()
        self.entities_by_yaml_filename = dict()

        for e in entities:
            self.append(e)

        # Tell all the entities to replace UUIDs with objects.
        self.replace_pointers_with_objects()

        self._setup_jinja()

    def __add__(self, other):

        if not isinstance(other, Bag):
            raise TypeError("Can't add %s" % other)

        title = "%s and %s" % (self.title, other.title)

        return Bag(
            title=title,
            entities=(list(self) + list(other)))

    def walk_through_elements(self):
        for el in self._elements:
            yield el

    def __iter__(self):
        return self.walk_through_elements()

    def __contains__(self, element):
        return element in self._elements

    def index(self, value):
        return self._elements.index(value)

    def _setup_jinja(self):

        # Figure out the path to the jinja2templates.
        jinja2dir = os.path.join(
            os.path.dirname(__file__), 'jinja2templates')

        self.e = jinja2.Environment(
            loader=jinja2.FileSystemLoader(jinja2dir))

        self.e.globals = {
            'clepy': clepy,
            'isinstance': isinstance,
            'hasattr': hasattr,
            'getattr': getattr,
            'enumerate': enumerate,
            'len': len,
            'colors':pitz.colors,
            'looper':tempita.looper,
        }

        if not hasattr(self, 'jinja_template'):
            self.jinja_template = 'bag.html'

    def to_csv(self, filepath, *columns):
        """
        Write out a CSV file for this bag listing the columns specified,
        AND the UUID at the very end.
        """

        columns = columns + ('uuid', )

        w = csv.writer(open(filepath, 'w'))
        w.writerow(columns)

        # I'm adding a blank line here between the column titles and the
        # data.
        w.writerow([])

        for e in self:
            row = []
            for col in columns:
                row += [e.get(col, '')]
            w.writerow(row)

    def __getitem__(self, i):
        """
        Allow lookups by index or uuid.
        """

        try:
            return self._elements[i]
        except TypeError:
            return self.by_uuid(i)

    def __delitem__(self, element):
        return self._elements.__delitem__(element)

    def __setitem__(self, index, element):
        return self._elements.__setitem__(index, element)

    def insert(self, index, element):
        return self._elements.insert(index, element)

    def __len__(self):
        return len(self._elements)

    def __getslice__(self, i, j):

        entities = self._elements.__getslice__(i, j)

        return Bag(title='slice from %s' % self.title,
            pathname=self.pathname, entities=entities,
            order_method=self.order_method, load_yaml_files=False,
            jinja_template=self.jinja_template,
            shell_mode=self.shell_mode)

    def sort(self, cmp=None, key=None, reverse=False):
        return self._elements.sort(cmp, key, reverse)

    def order(self, order_method=None):
        """
        Put all the entities into order based on either the order_method
        parameter or self.order_method.
        """

        if order_method:
            self.order_method = order_method

        if not self.order_method:
            raise ValueError("I need a method to order entities!")

        self.sort(cmp=self.order_method)

        return self

    def matches_dict(self, **d):

        matches = [e for e in self if e.matches_dict(**d)]

        return Bag(title='subset of %s' % self.title,
            pathname=self.pathname, entities=matches,
            order_method=self.order_method, load_yaml_files=False,
            jinja_template=self.jinja_template,
            shell_mode=self.shell_mode)

    def does_not_match_dict(self, **d):

        matches = [e for e in self if e.does_not_match_dict(**d)]

        return Bag(title='subset of %s' % self.title,
            pathname=self.pathname, entities=matches,
            order_method=self.order_method, load_yaml_files=False,
            jinja_template=self.jinja_template,
            shell_mode=self.shell_mode)

    def __call__(self, **d):
        """
        Now can just pass the filters right into the bag.
        """

        return self.matches_dict(**d)

    def by_uuid(self, obj):
        """
        Return an entity with uuid obj if we can.  Otherwise, return obj.
        """

        uuid = getattr(obj, 'uuid', obj)

        try:
            hash(obj)
        except TypeError:
            return obj

        try:
            return self.entities_by_uuid[uuid]

        except KeyError:

            frag = getattr(obj, 'frag', obj)
            try:
                return self.entities_by_frag[frag]
            except KeyError:
                return obj

    def by_frag(self, frag):
        return self.entities_by_frag[frag]

    def append(self, e, rerun_sort_after_append=True):
        """
        Put an entity in this bag and update related dictionaries.
        You can disable the sorting function if you set the
        rerun_sort_after_append to False.
        """

        # Don't add the same entity twice.
        if e.uuid not in self.entities_by_uuid:

            self._elements.append(e)
            self.entities_by_uuid[e.uuid] = e
            self.entities_by_frag[e.frag] = e
            self.entities_by_yaml_filename[e.yaml_filename] = e

            if rerun_sort_after_append:
                self.sort(self.order_method)

        return self

    def pop(self, index=-1):

        e = self._elements.pop(index)
        self.entities_by_uuid.pop(e.uuid)
        self.entities_by_frag.pop(e.frag)
        self.entities_by_yaml_filename.pop(e.yaml_filename)

        return e

    @property
    def pitzdir(self):
        return self.pathname

    @property
    def html_filename(self):

        return self._html_filename \
        or "%s.html" % quote_plus(self.title.lower())

    @property
    def summarized_view(self):
        s2 = "'%s' %s"

        return s2 % (
            self.title,
            self.contents)

    @property
    def shell_mode(self):
        return getattr(self, '_shell_mode', False)


    @property
    def colorized_detailed_view(self):

        self.order()

        self._setup_jinja()

        t = self.e.get_template('colorized_bag_detailed_view.txt')

        return t.render(bag=self,
            color=True,
            entities=self,
            shell_mode=self.shell_mode,
            entity_view='summarized_view')



    @property
    def detailed_view(self):

        self.order()

        self._setup_jinja()

        t = self.e.get_template('bag_detailed_view.txt')

        return t.render(bag=self, entities=self,
            color=False,
            shell_mode=self.shell_mode,
            entity_view='summarized_view')


    def custom_view(self, entity_view='summarized_view', color=False):
        """
        Print the entities using the entity view given.
        """

        self.order()

        self._setup_jinja()

        if color:
            t = self.e.get_template('colorized_bag_detailed_view.txt')

        else:
            t = self.e.get_template('bag_detailed_view.txt')

        return t.render(
            bag=self,
            entities=self,
            shell_mode=self.shell_mode,
            color=color,
            entity_view=entity_view)


    @property
    def contents(self):
        """
        Describe contents and the ordering method.

        >>> Bag().contents
        '(empty)'

        >>> from pitz.entity import Entity
        >>> Bag().append(Entity(title="blah")).contents
        '(1 entity entities)'
        """

        if self:

            nasty_list_comprehension = [
                '%d %s' % (typecount,

                    getattr(
                        globals().get(typename.title()),
                        'plural_name',
                        '%s entities' % typename))

                for typename, typecount in self.values('type')]

            if self.order_method.__doc__:

                return "(%s, ordered by %s)" \
                % (', '.join(nasty_list_comprehension),
                    self.order_method.__doc__)

            else:
                return "(%s)" % (', '.join(nasty_list_comprehension))


        else:
            return '(empty)'

    def __str__(self):
        return self.detailed_view

    def __repr__(self):
        return "<pitz.%s %s>" % (
            self.__class__.__name__,
            self.summarized_view)

    def replace_pointers_with_objects(self):
        """
        Tell all the entities inside to replace their pointers to
        objects with the objects themselves.
        """

        for e in self:
            if e.project:
                e.replace_pointers_with_objects()

    def replace_objects_with_pointers(self):
        """
        Just like replace_pointers_with_objects, but reversed.
        """
        for e in self:
            e.replace_objects_with_pointers()

    @property
    def attributes(self):
        """
        Return a sorted list of tuplies like (attribute, count) for all
        attributes in any entity in this bag.
        """

        dd = collections.defaultdict(int)

        for e in self:
            for a in e:
                dd[a] += 1

        return sorted(dd.items(), key=lambda t: t[1], reverse=True)

    def values(self, attr):
        """
        Return a sorted list of tuples like (value, count) for all the
        values for the attr.
        """
        dd = collections.defaultdict(int)

        for e in self:
            if attr in e:
                dd[e[attr]] += 1

        return sorted(
            [(e, c) for e, c in dd.items()],
            key=lambda t: t[1], reverse=True)

    def grep(self, phrase, ignore_case=False):
        """
        Return a new bag, filtering the entities in this bag by the ones
        that match the results of::

            $ grep phrase <files>

        where <files> are the files for all the entities in this bag.

        This function depends (of course) on files living in the
        filesystem and on a command-line program named grep.
        """

        if not self.pathname:
            raise ValueError("Sorry, I need a pathname first.")

        files = [os.path.join(self.pathname, f) for f in
            self.entities_by_yaml_filename]

        if not files:
            return self

        if ignore_case:
            cmd = ['grep', '-l', '-i', phrase]
        else:
            cmd = ['grep', '-l', phrase]

        cmd.extend(files)

        return Bag(title="entities matching grep %s" % phrase,
            pathname=self.pathname,
            order_method=self.order_method,

            entities=[
                self.entities_by_yaml_filename[os.path.basename(s.strip())]
                for s in subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout])

    def to_html(self, filepath):
        """
        Write this bag out as HTML to a file at filepath.
        """

        with open(os.path.join(filepath, self.html_filename), 'w') as f:
            f.write(self.html)

    def __getstate__(self):

        if hasattr(self, 'e'):
            delattr(self, 'e')

        return self.__dict__

    def __setstate__(self, d):

        self.__dict__.update(d)
        self._setup_jinja()

    @property
    def html(self):
        """
        Return a string containing this bag formatted as HTML.
        """

        tmpl = self.e.get_template(self.jinja_template)

        return tmpl.render(title=self.title, bag=self,
            isinstance=isinstance, UUID=UUID)

    @property
    def length(self):
        return len(self)

    @property
    def colorized_by_owner_view(self):

        return self.e.get_template(
            'colorized_by_owner_view.txt').render(
                bag=self)

    @property
    def by_owner_view(self):

        return self.e.get_template(
            'by_owner_view.txt').render(bag=self)
