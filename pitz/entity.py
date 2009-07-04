# vim: set expandtab ts=4 sw=4 filetype=python:

import logging, os, uuid
from datetime import datetime
from types import NoneType

import yaml

import jinja2

from pitz import edit_with_editor

log = logging.getLogger('pitz.entity')

class Entity(dict):

    """
    Acts like a regular dictionary with a few extra tweaks.
    """

    # When the value is None, I'll raise an exception unless the
    # attribute is defined.
    required_fields = dict(title=None)

    # Maps attributes to sequences of allowed values.
    allowed_values = dict()

    # Maps attributes to classes.  These attributes must be instances of
    # these classes.
    allowed_types = dict()

    # When these keys get updated, do not update the modified_time
    # key.
    do_not_update_modified_time_for_these_keys = [
        'yaml_file_saved', 'html_file_saved', 'modified_time',
    ]

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

        # Add this entity to the project (if we got a project).
        self.project = project
        if project is not None:
            self.project.append(self)
            self.replace_pointers_with_objects()

        # Set up a template loader.
        self.e = jinja2.Environment(
            loader=jinja2.PackageLoader('pitz', 'jinja2templates'))

        self.e.globals = {
            'isinstance':isinstance,
            'hasattr':hasattr,
        }

        self.update_modified_time = True


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

                super(Entity, self).__setitem__('modified_time', datetime.now())



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
        Return self or None, depending on whether we match.  You gotta
        match EVERYTHING in the passed-in dictionary.

        >>> e = Entity(title='Clean cat box', creator='Matt', 
        ...            tags=['boring', 'chore'])
        >>> e.matches_dict(creator='Matt') == e
        True
        >>> e.matches_dict(creator='Nobody') == None
        True
        >>> e.matches_dict(tags=['boring', 'chore']) == e
        True
        >>> e.matches_dict(tags='boring') == e
        True
        >>> e.matches_dict(tags='chore') == e
        True
        >>> e.matches_dict(creator=['Matt']) == e
        True
        >>> e.matches_dict(creator=['Matt', 'Nobody']) == e
        True
        >>> e.matches_dict(creator=['Matt', 'Nobody'],
        ...                tags=['fun']) == e
        False
        >>> e.matches_dict(creator=['Matt', 'Nobody'],
        ...                tags=['fun', 'boring']) == e
        True
        """

        for a, v in d.items():

            if self.project:

                # When v is a frag or a UUID, convert it to the object
                # it refers to.
                if v in self.project.entities_by_frag \
                or v in self.project.entities_by_uuid:

                    v = self.project[v]

            if a not in self: 
                return

            ev = self[a]
            
            if ev != v: 

                # Neither are lists, so don't bother doing anything else.
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
                and set(ev).isdisjoint(set(v)):
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


    def __str__(self):
        return self.detailed_view


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

        In other words, replaces the string "matt" with the object with
        "matt" as its uuid.
        """
        self.update_modified_time = False

        if self.project:

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

            if hasattr(val, 'uuid'):
                self[attr] = val.uuid

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

        self.replace_pointers_with_objects()

        return s


    @classmethod
    def from_yaml_file(cls, fp, project=None):

        """
        Loads the file at file path fp into the project and returns it.
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


class ImmutableEntity(Entity):

    """
    These can't be changed after instantiation.  Furthermore, if you try
    to make one that matches one that already exists, I'll return the
    original one.

    >>> ie1 = ImmutableEntity(title="a")
    >>> ie2 = ImmutableEntity(title="a")
    >>> id(ie1) == id(ie2)
    True
    >>> ie3 = ImmutableEntity(title="b")
    >>> id(ie1) == id(ie3)
    False
    """

    already_instantiated = dict()

    def __new__(cls, project=None, **kwargs):

        k = (('type', cls.__name__.lower()), ('title', kwargs['title']))

        if k in cls.already_instantiated:
            return cls.already_instantiated[k]

        else:

            o = super(ImmutableEntity, cls).__new__(cls, project, **kwargs)
            cls.already_instantiated[k] = o

            return o
