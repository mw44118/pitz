# vim: set expandtab ts=4 sw=4 filetype=python:

from __future__ import with_statement

import copy, logging, os, uuid, weakref
from datetime import datetime
from types import NoneType

import yaml

import jinja2

from clepy import edit_with_editor

from pitz.exceptions import NoProject

log = logging.getLogger('pitz.entity')


class MC(type):

    """
    This metaclass adds a dictionary named already_instantiated to the
    cls.
    """

    def __init__(cls, name, bases, d):
        cls.already_instantiated = weakref.WeakValueDictionary()


class Entity(dict):

    """
    Acts like a regular dictionary with some extra tweaks.

    When you give me a project and you try to instantiate something with
    a type and title that matches something that already exists, I'll
    return the original one.

    >>> from pitz.project import Project
    >>> p = Project(title="Blah")
    >>> ie1 = Entity(p, title="a")
    >>> ie2 = Entity(p, title="a")
    >>> id(ie1) == id(ie2)
    True
    >>> ie3 = Entity(p, title="b")
    >>> id(ie1) == id(ie3)
    False
    """

    __metaclass__ = MC

    # When the value is None, I'll raise an exception unless the
    # attribute is defined.
    required_fields = dict(title=None)

    # Maps attributes to sequences of allowed values.
    allowed_values = dict()

    # These attributes must be instances of these classes.
    allowed_types = dict()

    # When these keys get updated, do not update the modified_time
    # key.
    do_not_update_modified_time_for_these_keys = [
        'yaml_file_saved', 'html_file_saved', 'modified_time',
    ]


    def __new__(cls, project=None, **kwargs):

        """
        Checks if we already have something with this exact type and
        title.  If we do, then we just return that.

        If we don't have it, we make it and return it.
        """

        k = kwargs['title']

        if k in cls.already_instantiated:
            return cls.already_instantiated[k]

        else:
            o = super(Entity, cls).__new__(cls, project, **kwargs)
            cls.already_instantiated[k] = o

            return o


    def __setstate__(self, d):

        """
        Stuff loaded from the pickle file sidesteps both __new__ and
        __init__, so you can use this method to make sure some stuff
        happens.

        Because I've heavily hacked up how the yaml stuff works, __new__
        and __init__ still execute when loading from yaml.
        """

        self.__dict__.update(d)
        self._setup_jinja()

        # Now add this instance back in to the dictionary that maps
        # titles to instances.
        cls = self.__class__
        if self.title not in cls.already_instantiated:
            cls.already_instantiated[self.title] = self

        # Set some attributes that also get set in __init__.
        self.update_modified_time = True



    def __init__(self, project=None, **kwargs):

        self.update_modified_time = False

        # Make sure we got all the required fields.
        for rf, default_value in self.required_fields.items():

            if rf not in kwargs:

                # Use a default value if we got one.  
                if default_value is not None:

                    kwargs[rf] = default_value(project) \
                    if callable(default_value) \
                    else default_value

                # Otherwise, raise an exception.
                else:
                    raise ValueError("I need a value for %s!" % rf)

        # Originally, I tried using self.update here, but it seems that
        # update did NOT use my subclassed __setitem__ method.
        # If I were to subclass UserDict, then that would work, BUT
        # UserDict is not a new-style class, so I couldn't use super.
        for k, v in kwargs.items():
            self[k] = v

        self['type'] = self.__class__.__name__.lower()

        # Make a unique uuid if we don't already have one.
        if not self.get('uuid'):
            self['uuid'] = uuid.uuid4()

        self['frag'] = str(self['uuid'])[:6]

        # Handle attributes with defaults.
        if not self.get('created_time'):
            self['created_time'] = datetime.now() 

        if not self.get('modified_time'):
            self['modified_time'] = self['created_time']

        if not self.get('pscore'):
            self['pscore'] = 0

        self.project = project

        self._setup_jinja()

        self.update_modified_time = True


    def _get_project(self):
        return self._project


    def _set_project(self, p):

        if not hasattr(self, '_project'):
            self._project = None

        if p or not self._project:
            self._project = p

        if p is not None and self.uuid not in p.entities_by_uuid:
            p.append(self)
            if self.project:
                self.replace_pointers_with_objects()


    project = property(_get_project, _set_project)


    def _setup_jinja(self):
        # Set up a template loader.
        self.e = jinja2.Environment(
            loader=jinja2.PackageLoader('pitz', 'jinja2templates'))

        self.e.globals = {
            'isinstance':isinstance,
            'hasattr':hasattr,
        }


    def __setitem__(self, attr, val):

        """
        Make sure that the value is allowed for this attr before going
        any further.
        """

        if attr in self.allowed_values \
        and val not in self.allowed_values[attr]:

            raise ValueError("%s must be in %s, not %s!"
                % (attr, self.allowed_values[attr], val))

        elif attr in self.allowed_types \
        and not isinstance(val,
            (NoneType, uuid.UUID, self.allowed_types[attr])):

            raise TypeError("%s must be an instance of %s, not %s!"
                % (attr, self.allowed_types[attr], type(val)))

        else:
            super(Entity, self).__setitem__(attr, val)

            if self.update_modified_time \
            and attr not in self.do_not_update_modified_time_for_these_keys:

                super(Entity, self).__setitem__(
                    'modified_time', datetime.now())


    def __hash__(self):
        return self.uuid.int


    @property
    def yaml_filename(self):
        return '%(type)s-%(uuid)s.yaml' % self


    @property
    def frag(self):
        return self['frag']


    @property
    def uuid(self):
        return self['uuid']


    @property
    def title(self):
        return self['title']


    def matches_dict(self, **d):
        """
        Return self or None, depending on whether we match.

        You gotta match EVERYTHING in the passed-in dictionary, but the
        entity tries to match using a bunch of tricks.

        >>> e = Entity(title="blah", a=1)
        >>> e.matches_dict(a=1) == e
        True
        >>> e.matches_dict(a=2) == None
        True
        """

        for a, v in d.items():

            if a not in self:
                return

            # Possibly translate this object from its UUID/frag/title
            # representation to the actual object.

            if self.project:

                try:
                    hash(v)

                except TypeError:
                    v = v

                else:

                    # When v is a frag or a UUID, convert it to the object
                    # it refers to.
                    if v in self.project.entities_by_frag \
                    or v in self.project.entities_by_uuid:

                        v = self.project[v]

                    if a in self.allowed_types:
                        typename = self.allowed_types[a].__name__.lower()

                        results = self.project(type=typename, title=v)
                        if results.length == 1:
                            v = results[0]

            ev = self[a]
            
            # Do all this stuff when the entity has a different value
            # than the one passed in.
            if ev != v: 

                # Neither are lists, so don't bother doing anything
                # else.
                if not isinstance(ev, (list, tuple)) \
                and not isinstance(v, (list, tuple)):
                    return

                # ev is a list, v is a scalar, so check if v is in ev.
                if isinstance(ev, (list, tuple)) \
                and not isinstance(v, (list, tuple)) \
                and v not in ev:
                    return

                # ev is a scalar, v is a list.
                if not isinstance(ev, (list, tuple)) \
                and isinstance(v, (list, tuple)) \
                and ev not in v:
                    return
        
                # Both are lists, so test if ev intersects with v.
                if isinstance(ev, (list, tuple)) \
                and isinstance(v, (list, tuple)) \
                and not (set(ev) & set(v)):
                    return

        return self


    def does_not_match_dict(self, **d):
        """
        Returns self if ALL of the key-value pairs do not match.

        >>> e = Entity(title="blah", a=1, b=2)
        >>> e.does_not_match_dict(a=99, b=99, c=99) == e
        True
        >>> e.does_not_match_dict(a=1, b=1) == None
        True
        >>> e.does_not_match_dict(a=1) == None
        True
        >>> e.does_not_match_dict(c=1) == e
        True
        """

        for a, v in d.items():

            if a in self and self[a] == v:
                return

        return self


    def __repr__(self):
        return "<pitz.%s %s>" \
        % (self.__class__.__name__, self.summarized_view)


    @property
    def summarized_view(self):
        """
        Short description of the entity.
        """

        return "%(frag)s: %(title)s" % self

    @property
    def abbr(self):
        """
        Shortest possible description of entity.
        """

        if 'abbr' in self:
            return self['abbr']
        else:
            return self.title


    @property
    def detailed_view(self):
        """
        The detailed view of the entity.
        """

        d = dict()
        d.update(self)
        d['summarized_view'] = self.summarized_view
        d['line_of_dashes'] = "-" * len(self.summarized_view)
        d['type'] = self.__class__.__name__
        d['data'] = self

        t = self.e.get_template('entity_detailed_view.txt')

        return t.render(**d)


    @property
    def yaml(self):

        self.replace_objects_with_pointers()

        d = dict(self)
        d.pop('frag')

        y = yaml.dump(d, default_flow_style=False)

        # Now switch the pointers with the objects.
        if self.project:
            self.replace_pointers_with_objects()

        return y


    def __getstate__(self):

        self.replace_objects_with_pointers()
        d = self.copy()
        self.replace_pointers_with_objects()
        return d


    def to_yaml_file(self, pathname):
        """
        Returns the path of the file saved, IFF one got saved.

        The pathname specifies where to save it.
        """

        if self.stale_yaml:

            self['yaml_file_saved'] = datetime.now()

            fp = os.path.join(pathname, self.yaml_filename)
            f = open(fp, 'w')
            f.write(self.yaml)
            f.close()

            return fp 


    def replace_pointers_with_objects(self):

        """
        Replace pointer to entities with the entities that are pointed
        to.

        In other words, replace the uuid "matt" with the object that
        has "matt" as its uuid.
        """

        if not self.project:
            raise NoProject("I can't replace pointers without a project")

        self.update_modified_time = False

        for attr, val in self.items():

            # Skip over our own uuid attribute.
            if val == self.uuid:
                continue

            if isinstance(val, uuid.UUID):
                self[attr] = self.project.by_uuid(val)

        self.update_modified_time = True
        return self


    def replace_objects_with_pointers(self):
        """
        Replaces the value of an entity with just the string of the
        entity's uuid.

        In other words, replaces the object stored at sef['creator']
        with just the uuid of that object.
        """

        self.update_modified_time = False

        for attr, val in self.items():
            self[attr] = getattr(val, 'uuid', val)

        self.update_modified_time = True
        return self


    @property
    def html_filename(self):
        return "%(uuid)s.html" % self


    @property
    def stale_html(self):

        html_file_saved = self.get('html_file_saved',
            datetime(1991, 1, 1))

        return self['modified_time'] > html_file_saved


    def to_html_file(self, htmldir):

        if self.stale_html:

            self['html_file_saved'] = self['modified_time'] = datetime.now()

            filepath = os.path.join(htmldir, self.html_filename)

            with open(filepath, 'w') as f:
                f.write(self.html)

            return filepath
 

    @property
    def html(self):
        """
        Return a string of HTML representing this entity.
        """

        self.replace_objects_with_pointers()
        tmpl = self.e.get_template('entity.html')

        s = tmpl.render(title=self.title, entity=self,
            UUID=uuid.UUID)

        if self.project:
            self.replace_pointers_with_objects()

        return s


    @classmethod
    def from_yaml_file(cls, fp, project=None):

        """
        Returns an instance after loading yaml file fp.

        Remember, the instance might have pointers that need to be
        converted to proper references.
        """

        d = yaml.load(open(fp))

        if d:
            return cls(project, **d)


    def self_destruct(self, proj):
        """
        Remove this entity from the project.  Delete a yaml file if it
        exists.
        """

        # Remove this entity from the project.
        i = proj.index(self)
        proj.pop(i)

        # Delete any yaml file.
        if proj.pathname and os.path.isdir(proj.pathname):
            absolute_path = os.path.join(proj.pathname, self.yaml_filename)

            if os.path.exists(absolute_path):
                os.unlink(absolute_path)

        return self


    @property
    def stale_yaml(self):

        yaml_file_saved = self.get('yaml_file_saved',
            datetime(1991, 1, 1))

        return self['modified_time'] > yaml_file_saved


    def edit(self, attr):
        self[attr] = edit_with_editor(self.get(attr))


    def __cmp__(self, other):

        try:
            
            if 'pscore' not in other:
                return -1

            else:

                return cmp(
                    (self['pscore'], self['title']),
                    (other['pscore'], other['title']))

        except TypeError:
            return -1
