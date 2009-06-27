# vim: set expandtab ts=4 sw=4 filetype=python:

from collections import defaultdict
import csv, logging, os
from uuid import UUID, uuid4
from urllib import quote_plus

import jinja2

from pitz import *

logging.basicConfig(level=logging.INFO)


class Bag(list):

    """
    Bags are really just lists with some useful methods.
    """


    def __init__(self, title='', uuid=None, pathname=None, entities=(),
        order_method=by_created_time, **kwargs):

        self.title = title
        self.pathname = pathname
        self.order_method = order_method
        
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

        self.e = jinja2.Environment(
            loader=jinja2.PackageLoader('pitz', 'jinja2templates'))

        self.e.globals = {
            'isinstance':isinstance,
            'hasattr':hasattr,
            'enumerate':enumerate,
            'len':len,
        }
    

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
        Allow lookups by index or by uuid fragment.
        """

        try:
            return super(Bag, self).__getitem__(i)
        except TypeError:
            return self.by_uuid(i)


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
            order_method=self.order_method, load_yaml_files=False)

    def does_not_match_dict(self, **d):

        matches = [e for e in self if e.does_not_match_dict(**d)]

        return Bag(title='subset of %s' % self.title, 
            pathname=self.pathname, entities=matches,
            order_method=self.order_method, load_yaml_files=False)

    def __call__(self, **d):
        """
        Now can just pass the filters right into the bag.
        """

        return self.matches_dict(**d)


    def by_uuid(self, obj):
        """
        Return an entity with uuid obj if we can.  Otherwise, return uuid.
        """

        uuid = getattr(obj, 'uuid', obj)

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
        

    def append(self, e):
        """
        Put an entity in this bag and update related dictionaries.
        """

        # Don't add the same entity twice.
        if e.uuid not in self.entities_by_uuid:

            super(Bag, self).append(e)
            self.sort(self.order_method)
            self.entities_by_uuid[e.uuid] = e
            self.entities_by_frag[e.frag] = e
            self.entities_by_yaml_filename[e.yaml_filename] = e


    def pop(self, index=-1):

        e = super(Bag, self).pop(index)
        self.entities_by_uuid.pop(e.uuid)
        self.entities_by_frag.pop(e.frag)
        self.entities_by_yaml_filename.pop(e.yaml_filename)


    @property
    def html_filename(self):
        return "%s.html" % quote_plus(self.title.lower())

        
    @property
    def summarized_view(self):
        s2 = "<pitz.%s '%s' %s sorted by %s>"

        return s2 % (
            self.__class__.__name__,
            self.title,
            self.contents,
            self.order_method.__doc__)


    @property
    def detailed_view(self):

        # First sort the entitities just in case we've appended new
        # entities since the last time we sorted.
        self.order()

        t = self.e.get_template('bag_detailed_view.txt')

        return t.render(bag=self, entities=self)


    @property
    def contents(self):

        """
        Return a descriptive one-line string of the contents of the bag.
        """

        if self:
            return '(' + ', '.join(['%d %s entities' % (typecount, typename)
                for typename, typecount in self.values('type')]) +')'

        else:
            return '(empty)'


    def __str__(self):
        return self.detailed_view

    def __repr__(self):
        return self.summarized_view

    def replace_pointers_with_objects(self):
        """
        Tell all the entities inside to replace their pointers to
        objects with the objects themselves.
        """

        for e in self:
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

        dd = defaultdict(int)

        for e in self:
            for a in e:
                dd[a] += 1

        return sorted(dd.items(), key=lambda t: t[1], reverse=True)


    def values(self, attr):
        """
        Return a sorted list of tuples like (value, count) for all the
        values for the attr.
        """
        dd = defaultdict(int)

        for e in self:
            if attr in e:
                dd[e[attr]] += 1

        return sorted(dd.items(), key=lambda t: t[1], reverse=True)


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
            entities=[self.entities_by_yaml_filename[os.path.basename(s.strip())] 
                for s in subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout])


    def to_html(self, filepath):
        """
        Write this bag out as HTML to a file at filepath.
        """

        with open(filepath, 'w') as f:
            f.write(self.html)


    @property
    def html(self):
        """
        Return a string containing this bag formatted as HTML.
        """

        tmpl = self.e.get_template('bag.html')
        return tmpl.render(title=self.title, bag=self,
            isinstance=isinstance, UUID=UUID)

    @property
    def length(self):
        return len(self)
