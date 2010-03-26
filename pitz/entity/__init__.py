# vim: set expandtab ts=4 sw=4 filetype=python:

"""
The Entity class and Entity subclasses.
"""

# Lots of packages don't work on the app engine.
try:
    import shutil
except ImportError:
    shutil = None

import logging
import os
import re
import uuid
import weakref
from datetime import datetime
from types import NoneType

import jinja2
import yaml
from docutils.core import publish_parts
from docutils.utils import SystemMessage
import clepy

import pitz
from pitz import NoProject, by_descending_created_time
from pitz import by_whatever

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

    plural_name = 'entities'

    jinja_template = 'entity.html'

    cli_summarized_view_template = 'entity_summarized_view.txt'
    cli_detailed_view_template = 'entity_detailed_view.txt'
    cli_verbose_view_template = 'entity_verbose_view.txt'

    __metaclass__ = MC

    # When the value is None, I'll raise an exception when the
    # attribute is not defined.
    required_fields = dict(
        title=None,
        description='',
        pscore=0,
        attached_files=lambda proj: list(),
    )

    # Maps attributes to sequences of allowed values.
    allowed_values = dict()

    # These attributes must be instances of these classes.
    allowed_types = dict(
        pscore=int,
    )

    # When these keys get updated, do not update the modified_time
    # key.
    do_not_update_modified_time_for_these_keys = [
        'yaml_file_saved', 'html_file_saved', 'modified_time',
        'created_by',
    ]

    # Don't track activity on these attributes.
    do_not_track_activity_for_these_keys = [
        'yaml_file_saved', 'html_file_saved', 'modified_time',
        'created_by',
    ]

    def __new__(cls, project=None, **kwargs):
        """
        Checks if we already have something with this exact type and
        title.  If we do, then we just return that.

        If we don't have it, we make it and return it.
        """

        if 'title' not in kwargs:
            raise TypeError("%s requires a title!" % cls.__name__)

        title = kwargs['title']

        if title in cls.already_instantiated:
            return cls.already_instantiated[title]

        else:
            self = super(Entity, cls).__new__(cls, project, **kwargs)
            cls.already_instantiated[title] = self
            return self

    def __setstate__(self, d):
        """
        Stuff loaded from the pickle file sidesteps both __new__ and
        __init__, so you can use this method to make sure some stuff
        happens.

        Because I've heavily hacked up how the yaml stuff works, __new__
        and __init__ still execute when loading from yaml.
        """

        self._setup_jinja()

        # Add this instance in to the cls.already_instantiated
        # dictionary that maps titles to instances.
        cls = self.__class__
        if self.title not in cls.already_instantiated:
            cls.already_instantiated[self.title] = self

        # Set some attributes that also get set in __init__.

        self.update_modified_time = True
        self.record_activity_on_changes = True

    def __init__(self, project=None, **kwargs):

        self.update_modified_time = False
        self.record_activity_on_changes = False

        # Make sure we got all the required fields.
        for rf, default_value in self.required_fields.items():

            if rf not in kwargs and rf not in self:

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

        self.project = project

        self._setup_jinja()

        if hasattr(self.project, 'current_user') \
        and 'created_by' not in self:

            self['created_by'] = self.project.current_user

        self.update_modified_time = True
        self.record_activity_on_changes = True

    def _get_project(self):
        return getattr(self, '_project', None)

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

        # Figure out the path to the jinja2templates.
        jinja2dir = os.path.join(
            os.path.split(os.path.dirname(__file__))[0],
            'jinja2templates')

        # Set up a template loader.
        self.e = jinja2.Environment(
            extensions=['jinja2.ext.loopcontrols'],
            loader=jinja2.FileSystemLoader(jinja2dir))

        self.e.globals = {
            'clepy': clepy,
            'datetime': datetime,
            'os': os,
            'isinstance': isinstance,
            'hasattr': hasattr,
            'colors': pitz.colors,
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

        elif attr in self.allowed_types:

            allowed_type = self.allowed_types[attr]

            # Handle stuff like foo=[Entity] here.
            if isinstance(allowed_type, list) \
            and len(allowed_type) == 1 \
            and issubclass(allowed_type[0], Entity):

                cls = allowed_type[0]

                try:
                    iter(val)
                except TypeError:
                    raise TypeError(
                        "%s must be a list of %s instances, not %s!"
                        % (attr, cls, type(val)))

                for v in val:
                    if not isinstance(v, (NoneType, uuid.UUID, cls)):

                        raise TypeError(
                            "%s must be a list of %s instances, not %s!"
                            % (attr, cls, type(val)))


            # Handle stuff like foo=Entity here.
            elif not isinstance(val,
                (NoneType, uuid.UUID, allowed_type)):

                try:
                    val = allowed_type(val)

                except (TypeError, ValueError), ex:

                    raise TypeError("%s must be an instance of %s, not %s!"
                        % (attr, allowed_type, type(val)))

        self.maybe_update_modified_time(attr)
        self.maybe_record_activity(attr, val)

        # Finally, do the setitem.
        super(Entity, self).__setitem__(attr, val)

    def __hash__(self):
        """
        Necessary to allow Entity instances to be used as dictionary
        keys and set elements.
        """
        return self.uuid.int

    def custom_view(self, name_of_view=None,
        default_view='detailed_view', color=False):
        """
        Just a little nicer than writing all that getattr(...) stuff.
        """

        if name_of_view is None or not hasattr(self, name_of_view):
            return getattr(self, default_view)

        else:

            if color and hasattr(self, 'colorized_' + name_of_view):
                name_of_view = 'colorized_' + name_of_view

            return getattr(self, name_of_view)


    def maybe_update_modified_time(self, attr):

        if self.update_modified_time \
        and attr not in self.do_not_update_modified_time_for_these_keys:

            super(Entity, self).__setitem__(
                'modified_time', datetime.now())

    def maybe_record_activity(self, attr, val):

        if getattr(self, 'record_activity_on_changes', False) \
        and self.project \
        and self.project.me \
        and attr not in self.do_not_track_activity_for_these_keys:

            old_val = self.get(attr)

            activity_title = "%s set %s from %s to %s on %s" \
            % (self.project.me.abbr, attr,
                clepy.maybe_add_ellipses(str(old_val), 16),
                clepy.maybe_add_ellipses(str(val), 16),
                self.frag)

            return Activity(self.project, entity=self.uuid,
                title=activity_title,
                who_did_it=self.project.me,
                description='')

    def prioritize_above(self, other):
        """
        Set my pscore to the other entity's pscore + 1.
        """

        self['pscore'] = other['pscore'] + 1

    def prioritize_below(self, other):
        """
        Set my pscore to the other entity's pscore - 1.
        """

        self['pscore'] = other['pscore'] - 1

    def comment(self, who_said_it=None, title=None, description=None):
        """
        Store a comment on this entity.
        """

        if not who_said_it:

            if self.project and hasattr(self.project, 'me'):
                who_said_it = self.project.me

            else:
                who_said_it = Person.choose()

        if title is None:
            title = '''RE: task %(frag)s "%(title)s"''' % self

        if description is None:
            description = clepy.edit_with_editor("# Comment goes here")

        return Comment(self.project, entity=self.uuid, title=title,
            who_said_it=who_said_it, description=description)

    @property
    def pitzdir_replace_directive(self):

        if self.project:
            return ".. |pitzdir| replace:: %s" % self.project.pitzdir

    @property
    def comments(self):
        """
        Return all comments on this entity.
        """

        b = self.project(type='comment', entity=self)
        b.title = 'Comments on %(title)s' % self

        return b.order(by_descending_created_time)

    @property
    def activities(self):
        """
        Return all activities on this entity.
        """

        b = self.project(type='activity', entity=self)
        b.title = 'Activity on %(title)s' % self

        return b.order(by_whatever(
            'created_time (reversed)',
            'created_time', reverse=True))

    @property
    def yaml_filename(self):
        return '%(type)s-%(uuid)s.yaml' % self

    @property
    def frag(self):
        return self['frag']

    @property
    def colorized_frag(self):
        return (
            pitz.colors['dark_yellow'] +
            self.frag +
            pitz.colors['clear'])

    @property
    def uuid(self):
        return self['uuid']


    @property
    def title(self):
        return self['title']


    @property
    def description(self):
        return self['description']


    @property
    def attributes_view(self):

        t = self.e.get_template('entity_attributes_table.txt')
        return t.render(e=self)


    @property
    def description_view(self):

        t = self.e.get_template('description_view.txt')
        return t.render(e=self)


    @property
    def colorized_description_view(self):

        t = self.e.get_template('colorized_description_view.txt')
        return t.render(e=self)


    @property
    def description_excerpt(self):

        if self.description:
            return clepy.maybe_add_ellipses(
                self['description'].replace('\n', ' '), 66)

        else:
            return 'no description'

    @property
    def pscore(self):
        return self['pscore']


    @classmethod
    def choose_from_allowed_values(cls, attr, default=None):

        choices = sorted(cls.allowed_values[attr])

        print("Choose a value for %s" % attr)
        for i, e in enumerate(choices):
            print("%4d: %s" % (i + 1, getattr(e, 'summarized_view', e)))

        choice = raw_input(
            "Pick a %s or hit <ENTER> to choose %s: "
                % (
                    attr,
                    getattr(default, 'summarized_view', str(default))))

        try:
            return choices[int(choice)-1]

        except (TypeError, ValueError):
            return default

    @classmethod
    def choose(cls, default=None):

        choices = sorted(cls.already_instantiated.values(), reverse=True)

        print("Choose a %s" % cls.__name__)
        for i, e in enumerate(choices):
            print("%4d: %s" % (i + 1, getattr(e, 'summarized_view', e)))

        choice = raw_input(
            "Pick a %s or hit <ENTER> to choose %s: "
                % (
                    cls.__name__,
                    getattr(default, 'summarized_view', str(default))))

        try:
            return choices[int(choice)-1]

        except (TypeError, ValueError):
            return default

    choose_from_already_instantiated = choose

    @classmethod
    def choose_many_from_already_instantiated(cls):
        """
        Just like choose_from_already_instantiated, but allows many.
        """

        print("Pick a few %s" % cls.plural_name)

        choices = sorted(cls.already_instantiated.values(), reverse=True)

        for i, e in enumerate(choices):
            print("%4d: %s" % (i + 1, getattr(e, 'summarized_view', e)))

        print("Use commas or spaces to pick more than one.")

        temp = raw_input("Hit <ENTER> to not pick any.")

        if temp is None:
            return []

        results = []

        for choice in re.split(",| ", temp):

            if choice:

                e = choices[int(choice)-1]

                results.append(e)

        return results

    def what_they_really_mean(self, a, v):
        """
        Try to convert strings, UUIDs, and frags to more interesting
        objects.

        >>> bar = Entity(title='bar')
        >>> e = Entity(title='bogus entity')
        >>> e.allowed_types = {'foo':Entity, 'i':int}
        >>> e.what_they_really_mean('i', '99')
        99
        >>> bar == e.what_they_really_mean('foo', 'bar')
        True
        >>> [bar] == e.what_they_really_mean('foo', ['bar'])
        True
        >>> 'fizzle' == e.what_they_really_mean('baz', 'fizzle')
        True

        """

        if a not in self.allowed_types \
        or isinstance(v, Entity):
            return v

        if isinstance(v, uuid.UUID) and self.project:
            return self.project.by_uuid(v)

        if isinstance(v, basestring) and self.project \
        and v in self.project.entities_by_frag:

            return self.project.by_frag(v)

        at = self.allowed_types[a]

        if isinstance(at, list):
            inner_at = at[0]

            # When v is a title, look up an entity.
            if isinstance(v, basestring) \
            and v in inner_at.already_instantiated:

                return inner_at(title=v)

            # When v is a list, go through each element inside.
            elif isinstance(v, list):

                new_list = []
                for vv in v:

                    # is this gonna work?
                    new_list.append(self.what_they_really_mean(a, vv))

                return new_list

        elif issubclass(at, Entity):

            if isinstance(v, list):

                new_list = []
                for vv in v:

                    if isinstance(vv, Entity):
                        new_list.append(vv)

                    elif isinstance(vv, uuid.UUID) and self.project:
                        new_list.append(self.project.by_uuid(vv))

                    elif vv in at.already_instantiated:
                        new_list.append(at(title=vv))

                    elif isinstance(vv, basestring) and self.project \
                    and vv in self.project.entities_by_frag:

                        new_list.append(self.project.by_frag(vv))

                    else:
                        new_list.append(vv)

                return new_list

            else:

                if v in at.already_instantiated:
                    return at(title=v)

                else:
                    return v

        else:
            return at(v)

    def matches_dict(self, **d):
        """
        Return self or None, depending on whether we match all the
        key-value pairs.

        >>> e = Entity(title="blah", a=1, b=2, c=3)
        >>> e.matches_dict(a=1, c=3) == e
        True
        >>> e.matches_dict(a=2) == None
        True
        """

        for a, v in d.items():

            if a not in self:
                return

            v = self.what_they_really_mean(a, v)

            if self[a] != v:

                ev = self[a]

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
                and isinstance(v, (list, tuple)):

                    if ev not in v:

                        # Compare each element in v to ev.
                        for vv in v:

                            # Check UUIDs and frags.
                            if vv in self.project.entities_by_uuid \
                            or vv in self.project.entities_by_frag:

                                vv = self.project[vv]

                            # Now check typenames and titles.
                            typename = self.allowed_types[a].__name__ \
                            if a in self.allowed_types \
                            else None

                            results = self.project(
                                type=typename,
                                title=vv)

                            if results.length == 1:
                                vv = results[0]

                            if vv != ev:
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

        return "<pitz.%s %s %s>" % (
            self.__class__.__name__,
            self.frag,
            clepy.maybe_add_ellipses(self.title, 60))

    @property
    def html_summarized_view(self):
        """
        Return something like
            <a href="/entity/abc123">title</a>
        """

        safe_title = self.title.replace('<', '&lt;').replace('>', '&gt;')

        return (
            """<a href="/entity/%(uuid)s">%(safe_title)s</a>"""
            % dict(uuid=self.uuid, safe_title=safe_title))

    @property
    def one_line_view(self):
        """
        Shorter description, meant to fit within 72 characters.
        """

        return clepy.maybe_add_ellipses(
            "%(frag)s: %(title)s" % self,
            )


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
    def colorized_detailed_view(self):
        """
        Detailed view, but with colors!
        """

        return self.e.get_template(
            self.colorized_detailed_view_template).render(
                e=self)

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

        t = self.e.get_template(self.cli_detailed_view_template)

        return t.render(e=self, **d)

    @property
    def verbose_view(self):
        """
        Everything you could possibly want to know about this entity.
        """

        d = dict()
        d.update(self)
        d['summarized_view'] = self.summarized_view
        d['line_of_dashes'] = "-" * len(self.summarized_view)
        d['type'] = self.__class__.__name__
        d['data'] = self

        t = self.e.get_template(self.cli_verbose_view_template)

        return t.render(e=self, **d)

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

        """
        We want to pickle the pointers, not the objects, because lots of
        objects have reference cycles.
        """

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

    def save_attachment(self, filepath):
        """
        Save the file in filepath in the pitzdir.
        """

        if not shutil:
            raise NotImplementedError("Sorry, I need shutil for this")

        if not self.project:
            raise NoProject("I can't save attachments without a project.")

        attachment_folder = os.path.join(
            self.project.pathname, 'attached_files')

        if not os.path.isdir(attachment_folder):
            os.mkdir(attachment_folder)

        new_filepath = os.path.join(
            attachment_folder, os.path.basename(filepath))

        shutil.copy(filepath, new_filepath)

        if 'attached_files' not in self:
            self['attached_files'] = []

        self['attached_files'].append(new_filepath)

        return new_filepath

    def replace_pointers_with_objects(self):
        """
        Replace pointer to entities with the entities that are pointed
        to.

        In other words, replace the uuid "matt" with the object that
        has "matt" as its uuid.

        Also works when the values are lists and tuples of UUIDs.
        """

        if not self.project:
            raise NoProject("I can't replace pointers without a project")

        self.update_modified_time = False
        self.record_activity_on_changes = False

        for attr, val in self.items():

            # Skip over our own uuid attribute.
            if val == self.uuid:
                continue

            if isinstance(val, uuid.UUID):
                self[attr] = self.project.by_uuid(val)

            if isinstance(val, (list, tuple)):
                self[attr] = [self.project.by_uuid(x) for x in val]

        self.update_modified_time = True
        self.record_activity_on_changes = True
        return self

    def replace_objects_with_pointers(self):
        """
        Replaces the value of an entity with just the string of the
        entity's uuid.

        In other words, replaces the object stored at self['creator']
        with just the uuid of that object.
        """

        self.update_modified_time = False
        self.record_activity_on_changes = False

        for attr, val in self.items():
            self[attr] = getattr(val, 'uuid', val)

            if isinstance(val, (tuple, list)):
                self[attr] = [getattr(e, 'uuid', e) for e in val]

        self.update_modified_time = True
        self.record_activity_on_changes = True
        return self

    @property
    def html_filename(self):
        return "%(uuid)s.html" % self

    @property
    def stale_html(self):

        html_file_saved = self.get('html_file_saved',
            datetime(1991, 1, 1))

        return self['modified_time'] > html_file_saved

    def to_html_file(self, htmldir, force=False):
        """
        If force is True, then we ignore the timestamps.
        """

        if force or self.stale_html:

            self['html_file_saved'] = self['modified_time'] = datetime.now()

            filepath = os.path.join(htmldir, self.html_filename)

            f = open(filepath, 'w')

            f.write(self.html)
            f.close()

            return filepath

    @property
    def description_as_html(self):

        try:
            return publish_parts(self['description'],
                writer_name='html')['html_body']

        except SystemMessage, ex:

            log.error(
                "Couldn't render %(frag)s description as HTML"
                % self)

            log.exception(ex)

            return """<pre>%(description)s</pre>""" % self

    @property
    def html(self):
        """
        Return a string of HTML representing this entity.

        Convert the description attribute from restructured text into
        HTML.
        """

        self.replace_objects_with_pointers()
        tmpl = self.e.get_template(self.jinja_template)

        s = tmpl.render(title=self.title,
            description=self.description_as_html, entity=self,
            UUID=uuid.UUID, project=self.project)

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

        Return a list of yaml files deleted.
        """

        # Remove this entity from the project.
        i = proj.index(self)
        proj.pop(i)

        files_deleted = []

        # Delete any yaml file.
        if proj.pathname and os.path.isdir(proj.pathname):

            absolute_path = os.path.join(proj.pathname, self.yaml_filename)

            if os.path.exists(absolute_path):
                os.unlink(absolute_path)
                files_deleted.append(absolute_path)

            for a in self.activities:
                files_deleted.extend(a.self_destruct(proj))

            for c in self.comments:
                files_deleted.extend(c.self_destruct(proj))

        return files_deleted

    @property
    def stale_yaml(self):

        yaml_file_saved = self.get('yaml_file_saved',
            datetime(1991, 1, 1))

        return self['modified_time'] > yaml_file_saved

    def edit(self, attr):
        """
        if attr is in the allowed_types dictionary, and the allowed type
        is an Entity subclass, then show a list of all instances of the
        subclass and ask for a choice.

        Otherwise, open an editor with the value for this attr.
        """

        if attr in self.allowed_types:
            allowed_type = self.allowed_types[attr]

            # Handle stuff like foo=[Entity] here.
            if isinstance(allowed_type, list) \
            and len(allowed_type) == 1 \
            and issubclass(allowed_type[0], Entity):

                self[attr] = allowed_type[0]\
                .choose_many_from_already_instantiated()


            # Handle stuff like foo=Entity here.
            elif issubclass(allowed_type, Entity):

                self[attr] = \
                allowed_type.choose_from_already_instantiated()

        else:
            self[attr] = clepy.edit_with_editor(self.get(attr))

        return self

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


class Estimate(Entity):

    plural_name = 'estimates'

    required_fields = dict(
        title=None,
        description='',
        pscore=0,
        points=0)

    allowed_types = dict(
        pscore=int,
        points=int)

    # Maybe this should be a dictionary of bags, not a dictionary of
    # lists.
    ranges = [

        ("Matt's choice", [
            dict(title='trivial', points=1, pscore=100),
            dict(title='straightforward', points=2, pscore=90),
            dict(title='difficult', points=4, pscore=80),
            dict(title='maybe impossible', points=4, pscore=70)]),

        ("easy-medium-hard", [
            dict(title='easy', points=1, pscore=100),
            dict(title='medium', points=2, pscore=90),
            dict(title='hard', points=3, pscore=80)]),

        ("one to ten points", [
            dict(title=i, points=i, pscore=(100 - i * 10))
            for i in xrange(1, 11)]),
    ]

    def __str__(self):
        return self.title

    @property
    def tasks(self):
        """
        Return tasks with this estimate.
        """

        if not self.project:
            raise NoProject("Need a self.project for this!")

        else:
            return self.project.tasks(estimate=self)

    @property
    def points(self):
        return self['points']

    @classmethod
    def choose_estimate_range(cls):
        """
        Print all the estimate ranges available and ask for a choice.

        Returns a bag of estimates if a range was chosen.
        """

        print("Choose from any of:")

        for num, (title, values) in enumerate(cls.ranges):

            s = "%s." % (num + 1)
            print("%-3s %s" % (s, title))

            for val in values:
                print("    *   %(title)s (%(points)s points)" % val)

            print("")

        choice = raw_input(
            "Choose a number, or hit ENTER to do nothing: ").strip()

        if choice:
            return cls.ranges[int(choice)-1]

    @classmethod
    def add_range_of_estimates_to_project(cls, proj, range):
        """
        Add all estimates in the range to the project.
        """

        title, values = range
        for val in values:
            est = cls(proj, **val)

        return proj


class Status(Entity):

    plural_name = 'statuses'

    def __str__(self):
        return self.title

    @property
    def tasks(self):
        """
        Return tasks with this status
        """

        if not self.project:
            raise NoProject("Need a self.project for this!")

        else:
            return self.project.tasks(status=self)

    @classmethod
    def setup_defaults(cls, proj):
        """
        Create a few statuses, like started, unstarted, finished,
        and abandoned.
        """

        for title, pscore in [
            ('finished', 100),
            ('started', 50),
            ('paused', 40),
            ('queued', 30),
            ('unstarted', 20),
            ('abandoned', 10),
            ]:

            cls(proj, title=title, pscore=pscore)


class Milestone(Entity):
    """
    Useful for bundling tasks
    """

    required_fields = dict(
        title=None,
        description='',
        pscore=0,
        reached=False,
    )

    allowed_values = dict(
        reached=[False, True],
    )

    plural_name = "milestones"

    jinja_template = 'milestone.html'

    def __str__(self):
        return self.title

    @property
    def tasks(self):

        if not self.project:
            raise NoProject("I need a project before I can look up tasks!")

        tasks = self.project(type='task', milestone=self)
        tasks.title = 'Tasks in %(title)s' % self
        return tasks

    @property
    def todo(self):

        unfinished = self.tasks.does_not_match_dict(
            status=Status(title='finished'))\
        .does_not_match_dict(status=Status(title='abandoned'))

        unfinished.title = "Unfinished tasks in %(title)s" % self
        return unfinished

    @property
    def summarized_view(self):
        """
        One-line description of the milestone
        """

        started = Status(title='started')
        finished = Status(title='finished')
        unstarted = Status(title='unstarted')

        a = self.tasks(status=finished).length
        b = self.tasks(status=[finished, started, unstarted]).length

        if b is not 0:
            pct_complete = 100 * (float(a) / b)
        else:
            pct_complete = 0.0

        d = {
            'frag': self['frag'],
            'title': self['title'],
            'pct_complete': pct_complete,
            'num_finished_tasks': a,
            'num_tasks': b}

        s = (
            "%(frag)s %(title)s: %(pct_complete)0.0f%% complete"
            " (%(num_finished_tasks)d / %(num_tasks)d tasks)")
        return s % d


class Tag(Entity):

    plural_name = "tags"
    jinja_template = 'tag.html'

    @property
    def tasks(self):

        if not self.project:
            raise NoProject(
                "I need a project before I can look up tasks!")

        tasks = self.project(type='task', tags=self)
        tasks.title = 'Tasks in %(title)s' % self

        return tasks


class Component(Entity):

    plural_name = "components"

    jinja_template = 'component.html'

    @property
    def tasks(self):

        if not self.project:
            raise NoProject(
                "I need a project before I can look up tasks!")

        tasks = self.project(type='task', components=self)
        tasks.title = 'Tasks in %(title)s' % self

        return tasks

    @property
    def todo(self):

        unfinished = self.tasks.does_not_match_dict(
            status=Status(title='finished'))\
        .does_not_match_dict(status=Status(title='abandoned'))

        unfinished.title = "Unfinished tasks in %(title)s" % self
        return unfinished


class Comment(Entity):
    """
    You can comment on any entity.
    """

    plural_name = "comments"

    required_fields = dict(
        title=None,
        description='',
        pscore=0,
        who_said_it=None,
        entity=None,
    )

    @property
    def summarized_view(self):
        """
        Shorter description of the comment.
        """

        title = clepy.maybe_add_ellipses(
            self['title'].strip().replace('\n', ' '), 65)

        if self['description']:
            description_excerpt = clepy.maybe_add_ellipses(
                self['description'].strip().replace('\n', ' ')) + '\n'

        else:
            description_excerpt = ''

        frag = self['frag']

        author = self['who_said_it']
        who_said_it = getattr(author, 'title', author)

        how_long_ago = clepy.time_ago(self['created_time'])

        return self.e.get_template(
            'comment_summarized_view.txt').render(locals())

    @property
    def detailed_view(self):

        title = self['title'].strip().replace('\n', '  ')
        who_said_it = self['who_said_it']
        who_said_it = getattr(who_said_it, 'title', who_said_it)

        time = self['created_time'].strftime(
            "%A, %B %d, %Y, at %I:%M %P")

        description = self.description

        return self.e.get_template(
            'comment_detailed_view.txt').render(locals())

from pitz.entity.person import Person

class Activity(Entity):
    """
    Tracks interesting changes to the data model.
    """

    plural_name = "activities"

    required_fields = dict(
        title=None,
        description='',
        pscore=0,
        who_did_it=None,
        entity=None,
    )

    allowed_types = dict(
        who_did_it=Person,
        entity=Entity,
    )

    @property
    def summarized_view(self):

        return '%s (%s)' % (
            self,
            clepy.time_ago(self['created_time']))

from pitz.entity.task import Task
