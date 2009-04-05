# vim: set expandtab ts=4 sw=4 filetype=python:

from collections import defaultdict
import logging, os, uuid
from glob import glob

import yaml
import jinja2

from pitz.entity import Entity
from pitz.task import Task
from pitz.person import Person

logging.basicConfig(level=logging.INFO)

def by_whatever(func_name, *whatever):
    """
    Returns a function suitable for sorting, using whatever.

    >>> e1, e2 = {'a':1, 'b':1, 'c':2}, {'a':2, 'b':2, 'c':1}
    >>> by_whatever('xxx', 'a')(e1, e2)
    -1
    >>> by_whatever('xxx', 'c', 'a')(e1, e2)
    1
    """

    def f(e1, e2):

        return cmp(
            [e1.get(w) for w in whatever],
            [e2.get(w) for w in whatever])

    f.__doc__ = "by_whatever(%s)" % list(whatever)
    f.func_name = func_name
        
    return f

by_spiciness = by_whatever('by_spiciness', 'peppers')
by_created_time = by_whatever('by_created_time', 'created_time')

by_type_status_created_time = by_whatever('by_type_status_created_time', 
    'type', 'status', 'created time')

class Bag(object):
    """
    Really just a collection of entities with a name on it.  
    """

    def __init__(self, title='', name=None, pathname=None, entities=(), 
        order_method=by_created_time, load_yaml_files=True):

        # print("Locals in Bag.__init__: %s" % locals())

        self.title = title
        self.entities = list()
        self.pathname = pathname
        self.order_method = order_method
        
        if name:
            self.name = name

        # Make a unique name if we didn't get one.
        if not name:
            self.name = '%s-%s' % (self.__class__.__name__.lower(), 
                uuid.uuid4())

        # These will get populated in self.append.
        self.entities_by_name = dict()

        for e in entities:
            self.append(e)

        # Only load from the file system if we don't have anything.
        if self.pathname and load_yaml_files:
            self.load_entities_from_yaml_files()

        # Finally, tell all the entities to replace pointers with
        # objects.
        self.replace_pointers_with_objects()

    @property
    def yaml(self):
        """
        Return a block of yaml.
        """

        data = dict(
            title=self.title,
            order_method_name=self.order_method.func_name,
            name=self.name,
            pathname=self.pathname,
            )

        return yaml.dump(data, default_flow_style=False)


    def __iter__(self):
        """
        Make it possible to do "for entity in bag".
        """

        for e in self.entities:
            yield e

    def __getitem__(self, i):
        return self.entities[i]

    def __len__(self):
        return len(self.entities)

    def order(self, order_method=None):

        """
        Put all the entities into order based on either the order_method
        parameter or self.order_method.
        """

        if order_method:
            self.order_method = order_method

        if not self.order_method:
            raise ValueError("I need a method to order entities!")

        self.entities.sort(cmp=order_method)

    def matches_dict(self, **d):
        
        matches = [e for e in self.entities if e.matches_dict(**d)]

        return Bag(title='subset of %s' % self.title, 
            pathname=self.pathname, entities=matches,
            order_method=self.order_method, load_yaml_files=False)

    def does_not_match_dict(self, **d):

        matches = [e for e in self.entities if e.does_not_match_dict(**d)]

        return Bag(title='subset of %s' % self.title, 
            pathname=self.pathname, entities=matches,
            order_method=self.order_method, load_yaml_files=False)

    def __call__(self, **d):
        """
        Now can just pass the filters right into the bag.
        """

        return self.matches_dict(**d)

    def matching_pairs(self, pairs):
        """
        For pairs like

            [
                ('type', 'task'),
                ('assigned-to', 'person-matt'),
            ]

        return a new bag instance containing all entities that match.
        """

        matches = [e for e in self if e.matches_pairs(pairs)]
        return Bag(pathname=self.pathname, entities=matches,
            order_method=self.order_method)

    def by_name(self, name):
        """
        Return an entity named name if we can.  Otherwise, return name.
        """

        if isinstance(name, Entity):
            name = name.name

        return self.entities_by_name.get(name, name)

    def append(self, e):
        """
        Put an entity in this bag.

        This possibly destroys the sorted order, so you may want to run
        self.order() next.
        """

        # Don't add the same entity twice.
        if e.name not in self.entities_by_name:

            self.entities.append(e)
            self.entities.sort(self.order_method)
            self.entities_by_name[e.name] = e

    def to_yaml_file(self, pathname=None):
        """
        Save this bag to a YAML file.
        """

        if not pathname \
        and not self.pathname \
        and not os.path.isdir(self.pathname):
            raise ValueError("I need a pathname!")

        pathname = pathname or self.pathname

        fp = os.path.join(pathname, '%s.yaml' % (self.name)) 
        f = open(fp, 'w')
        f.write(self.yaml)
        f.close()
        logging.debug("Saved file %s" % fp)

        return fp

    @classmethod
    def from_yaml_file(cls, fp): 
        d = yaml.load(open(fp))

        # Dig out the string that points to the order method and replace
        # it with the actual function.

        d['order_method'] = globals()[d['order_method_name']]
        d.pop('order_method_name')

        return cls(**d)
        

    def save_entities_to_yaml_files(self, pathname=None):
        """
        Tell every entity to write itself out to YAML.
        """

        if not pathname \
        and not self.pathname \
        and not os.path.isdir(self.pathname):
            raise ValueError("I need a pathname!")

        pathname = pathname or self.pathname

        # Send all the entities to the filesystem.
        return [e.to_yaml_file(pathname) 
            for e in self.entities]


    def load_entities_from_yaml_files(self, pathname=None):
        """
        Loads all the files matching pathglob into this bag.
        """

        if pathname:
            self.pathname = pathname

        if not self.pathname:
            raise ValueError("I need a path to the files!")

        if not os.path.isdir(self.pathname):
            raise ValueError("%s isn't a directory." % self.pathname)

        pathglob = os.path.join(self.pathname, '*.yaml')

        for fp in glob(pathglob):

            bn = os.path.basename(fp)

            if bn.startswith('task-'):
                Task.from_yaml_file(fp, self)

            elif bn.startswith('person-'):
                Person.from_yaml_file(fp, self)

            elif bn.startswith('milestone-'):
                Milestone.from_yaml_file(fp, self)

            elif bn.startswith('component-'):
                Component.from_yaml_file(fp, self)

        return self

    @property
    def summarized_view(self):
        return repr(self)

    @property
    def detailed_view(self):

        # First sort the entitities just in case we've appended new
        # entities since the last time we sorted.
        self.entities.sort(self.order_method)

        t = jinja2.Template("""\
{%  for dash in bag.title -%}={% endfor %}
{{ bag.title }}
{%  for dash in bag.title -%}={% endfor %}

{{ bag.contents }}
{%  for dash in bag.contents -%}-{% endfor %}

{% for i, e in enumerate(entities) -%}
{{ "%4d" | format(i) }}: {{e.summarized_view}}
{% endfor %}""")

        return t.render(bag=self, entities=self.entities, 
            enumerate=enumerate, len=len)

    @property
    def contents(self):

        if self:
            return '(' + ', '.join(['%d %s entities' % (typecount, typename) 
                for typename, typecount in self.values('type')]) +')'

        else:
            return '(empty)'

    def __str__(self):
        return self.detailed_view

    def __repr__(self):

        s2 = "<pitz.%s '%s' %s sorted by %s>"

        return s2 % (
            self.__class__.__name__,
            self.title,
            self.contents,
            self.order_method.__doc__,
            )


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

        for e in self.entities:
            for a in e.keys():
                dd[a] += 1

        return sorted(dd.items(), key=lambda t: t[1], reverse=True)

    def values(self, attr):
        """
        Return a sorted list of tuples like (value, count) for all the
        values for the attr.
        """
        dd = defaultdict(int)

        for e in self.entities:
            if attr in e:
                dd[e[attr]] += 1

        return sorted(dd.items(), key=lambda t: t[1], reverse=True)
