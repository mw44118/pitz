# vim: set expandtab ts=4 sw=4 filetype=python:

"""
The Entity class and Entity subclasses.
"""

from __future__ import with_statement

import copy, logging, os, re, shutil, textwrap, uuid, weakref
from datetime import datetime
from types import NoneType

import jinja2, tempita, yaml

from docutils.core import publish_parts
from docutils.utils import SystemMessage

import clepy

from pitz import NoProject

from pitz import by_created_time

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

    >>> from pitz.bag import Project
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
    ]


    def __new__(cls, project=None, **kwargs):

        """
        Checks if we already have something with this exact type and
        title.  If we do, then we just return that.

        If we don't have it, we make it and return it.
        """

        if 'title' not in kwargs:
            raise TypeError("%s requires a title!" % cls.__name__)

        k = kwargs['title']

        if k in cls.already_instantiated:

            o = cls.already_instantiated[k]
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

        self._setup_jinja()

        # Add this instance in to the cls.already_instantiated
        # dictionary that maps titles to instances.
        cls = self.__class__
        if self.title not in cls.already_instantiated:
            cls.already_instantiated[self.title] = self

        # Set some attributes that also get set in __init__.

        self.update_modified_time = True


    def __init__(self, project=None, **kwargs):

        self.update_modified_time = False

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
            autoescape=True,
            extensions=['jinja2.ext.loopcontrols'],
            loader=jinja2.PackageLoader('pitz', 'jinja2templates'))

        self.e.globals = {
            'datetime':datetime,
            'os':os,
            'isinstance':isinstance,
            'hasattr':hasattr,
            'looper':tempita.looper,
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

            try:
                val = self.allowed_types[attr](val)

            except (TypeError, ValueError), ex:

                raise TypeError("%s must be an instance of %s, not %s!"
                    % (attr, self.allowed_types[attr], type(val)))


        # Now that we made it through the gauntlet, do the assignment.

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


    @property
    def description(self):
        return self['description']


    @property
    def pscore(self):
        return self['pscore']


    @classmethod
    def choose_from_allowed_values(cls, attr, default=None):

        choices = sorted(cls.allowed_values[attr])

        print("Choose a value for %s" % attr)
        for i, e in enumerate(choices):
            print("%4d: %s" % (i+1, getattr(e, 'summarized_view', e)))

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
            print("%4d: %s" % (i+1, getattr(e, 'summarized_view', e)))

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
            print("%4d: %s" % (i+1, getattr(e, 'summarized_view', e)))

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
        return "<pitz.%s %s>" % (self.__class__.__name__, self.title)


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

        for attr, val in self.items():

            # Skip over our own uuid attribute.
            if val == self.uuid:
                continue

            if isinstance(val, uuid.UUID):
                self[attr] = self.project.by_uuid(val)

            if isinstance(val, (list, tuple)):
                self[attr] = [self.project.by_uuid(x) for x in val]

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

            if isinstance(val, (tuple, list)):
                self[attr] = [getattr(e, 'uuid', e) for e in val]

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


    def to_html_file(self, htmldir, force=False):
        """
        If force is True, then we ignore the timestamps.
        """

        if force or self.stale_html:

            self['html_file_saved'] = self['modified_time'] = datetime.now()

            filepath = os.path.join(htmldir, self.html_filename)

            with open(filepath, 'w') as f:
                f.write(self.html)

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

        """
        if attr points to an Entity subclass, then show a list of all
        instances of the subclass and ask for a choice.

        Otherwise, open an editor with the value for this attr.
        """

        if issubclass(self.allowed_types.get(attr, object), Entity):
            self[attr] = self.allowed_types[attr].choose()

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

        finished = Status(title='finished')

        a = self.tasks(status=finished).length
        b = self.tasks.length

        if b is not 0:
            pct_complete = 100*(float(a)/b)
        else:
            pct_complete = 0.0

        d = {
            'frag':self['frag'],
            'title':self['title'],
            'pct_complete':pct_complete,
            'num_finished_tasks':a,
            'num_tasks': b}

        s = "%(frag)s %(title)s: %(pct_complete)0.0f%% complete (%(num_finished_tasks)d / %(num_tasks)d tasks)"
        return s % d


class Person(Entity):

    """
    Track who is doing what.
    """

    plural_name = "people"


    def save_as_me_yaml(self):

        """
        Designate this person is me by saving a me.yaml file.
        """

        if not self.project:
            raise NoProject("Sorry, saving a me.yaml needs a project")

        me_yaml_path = os.path.join(self.project.pathname, 'me.yaml')
        me_yaml = open(me_yaml_path, 'w')
        me_yaml.write(yaml.dump(self.uuid))

        return me_yaml_path


class Task(Entity):

    plural_name = "tasks"

    allowed_types = dict(
        owner=Person,
        points=int,
        milestone=Milestone,
        status=Status,
        estimate=Estimate)

    required_fields = dict(
        title=None,
        description='',
        pscore=0,
        milestone=lambda proj: Milestone(proj, title='unscheduled'),
        status=lambda proj: Status(proj, title='unstarted'),
        estimate=lambda proj: Estimate(proj, title='not estimated'),
        components=lambda proj: list(),
    )

    jinja_template = 'task.html'

    @property
    def milestone(self):
        return self['milestone']


    @property
    def status(self):
        return self['status']


    @property
    def estimate(self):
        return self['estimate']

    @property
    def html_summarized_view(self):

        return "%s (%s)""" % (
            super(Task, self).html_summarized_view,
            self['status'].html_summarized_view)

    @property
    def summarized_view(self):
        """
        Short description of the task.
        """

        frag = self['frag']
        title = clepy.maybe_add_ellipses(self.title, 45)

        status = '(%s)' % getattr(self['status'], 'abbr', self['status'])

        if 'milestone' in self:
            milestone = getattr(self['milestone'], 'abbr', self['milestone'])
        else:
            milestone = '...'

        pscore = self['pscore']

        return "%(frag)6s  %(title)-48s  %(milestone)3s  %(status)-11s" \
        % locals()


    @property
    def comments(self):
        """
        Return all comments on this task.
        """

        b = self.project(type='comment', entity=self)
        b.title = 'Comments on %(title)s' % self

        return b.order(by_created_time)


    def abandon(self):

        if self['status'].title in ['unstarted', 'started']:
            self['status'] = Status(title='abandoned')
            return self

        else:
            raise ValueError('You can only abandon unstarted or started tasks.')


    def start(self):

        if self['status'].title in ['unstarted', 'abandoned']:
            self['status'] = Status(title='started')
            return self

        else:
            raise ValueError(
                'You can only start unstarted or abandoned tasks.')


    def finish(self):

        self['status'] = Status(title='finished')
        return self


    def comment(self, who_said_it=None, title=None, description=None):

        """
        Store a comment on this task.
        """

        if not who_said_it:

            if self.project and hasattr(self.project, 'me'):
                who_said_it = self.project.me

            else:
                who_said_it = Person.choose()

        if not title:
            title = '''RE: task %(frag)s "%(title)s"''' % self

        if not description:
            description = clepy.edit_with_editor("# Comment goes here")

        return Comment(self.project, entity=self.uuid, title=title,
            who_said_it=who_said_it, description=description)


    def assign(self, owner):

        self['owner'] = owner


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

        title = self['title'].strip().replace('\n', ' ')
        title = "%s..." % title[:60] if len(title) > 60 else title

        who_said_it = self['who_said_it']
        who_said_it = getattr(who_said_it, 'title', who_said_it)

        return "%(who_said_it)s said: %(title)s" % dict(
            who_said_it=who_said_it,
            time=self['created_time'].strftime("%I:%M %P, %a, %m/%d/%y"),
            title=title,
        )


    @property
    def detailed_view(self):

        title = textwrap.fill(self['title'].strip().replace('\n', '  '))
        who_said_it = self['who_said_it']
        who_said_it = getattr(who_said_it, 'title', who_said_it)
        time = self['created_time'].strftime("%A, %B %d, %Y, at %I:%M %P")
        description = self.description
        tmpl = self.e.get_template('comment_detailed_view.txt')

        return tmpl.render(locals())




class Component(Entity):

    plural_name = "components"

    jinja_template = 'component.html'

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
