# vim: set expandtab ts=4 sw=4 filetype=python:

"""
Bags and Bag subclasses.
"""

from __future__ import with_statement

from collections import defaultdict
import csv, glob, logging, os, pickle
from uuid import UUID, uuid4
from urllib import quote_plus

import clepy, jinja2, pkg_resources, tempita

from pitz.entity import *
from pitz import *

log = logging.getLogger('pitz.bag')


class Bag(list):

    """
    Bags are really just lists with some useful methods.
    """


    def __init__(self, title='', html_filename=None, uuid=None,
        pathname=None, entities=(),
        order_method=by_pscore_and_milestone, **kwargs):

        self.title = title
        self.pathname = pathname
        self.order_method = order_method
        self._html_filename = html_filename
        
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


    def _setup_jinja(self):

        self.e = jinja2.Environment(
            loader=jinja2.PackageLoader('pitz', 'jinja2templates'))

        self.e.globals = {
            'isinstance':isinstance,
            'hasattr':hasattr,
            'enumerate':enumerate,
            'len':len,
            'looper':tempita.looper,
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
        Allow lookups by index or uuid.
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
        Return an entity with uuid obj if we can.  Otherwise, return obj.
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


    def append(self, e, rerun_sort_after_append=True):
        """
        Put an entity in this bag and update related dictionaries.
        You can disable the sorting function if you set the
        rerun_sort_after_append to False.
        """

        # Don't add the same entity twice.
        if e.uuid not in self.entities_by_uuid:

            super(Bag, self).append(e)
            self.entities_by_uuid[e.uuid] = e
            self.entities_by_frag[e.frag] = e
            self.entities_by_yaml_filename[e.yaml_filename] = e

            if rerun_sort_after_append:
                self.sort(self.order_method)

        return self


    def pop(self, index=-1):

        e = super(Bag, self).pop(index)
        self.entities_by_uuid.pop(e.uuid)
        self.entities_by_frag.pop(e.frag)
        self.entities_by_yaml_filename.pop(e.yaml_filename)

        return e


    @property
    def html_filename(self):

        return self._html_filename \
        or "%s.html" % quote_plus(self.title.lower())

        
    @property
    def summarized_view(self):
        s2 = "'%s' %s sorted by %s"

        return s2 % (
            self.title,
            self.contents,
            self.order_method.__doc__)


    @property
    def detailed_view(self):

        self.order()

        self._setup_jinja()

        t = self.e.get_template('bag_detailed_view.txt')
        return t.render(bag=self, entities=self)


    @property
    def contents(self):

        """
        Return string describing contents of the bag.

        >>> Bag().contents
        '(empty)'

        >>> Bag().append(Entity(title="blah")).contents
        '(1 entity entities)'
        """

        if self:

            nasty_list_comprehension = [
                '%d %s' % (typecount,

                    getattr(
                        getattr(self, 'classes', {}).get(typename),
                        'plural_name',
                        '%s entities' % typename))

                for typename, typecount in self.values('type')]

            return "(%s)" % ', '.join(nasty_list_comprehension)

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

        tmpl = self.e.get_template('bag.html')
        return tmpl.render(title=self.title, bag=self,
            isinstance=isinstance, UUID=UUID)


    @property
    def length(self):
        return len(self)


class Project(Bag):

    """
    The project is the bag that everybody should track, because it is
    the only thing that keeps references to every other thing.
    """

    # These are all the classes that I will try to instantiate when
    # reading yaml files.
    classes = dict(
        entity=Entity,
        status=Status,
        estimate=Estimate,
        task=Task,
        person=Person,
        milestone=Milestone,
        comment=Comment,
        component=Component)


    def __init__(self, title='', uuid=None, pathname=None, entities=(),
        order_method=by_pscore_and_milestone, load_yaml_files=True,
        **kwargs):

        self.rerun_sort_after_append = True

        super(Project, self).__init__(title, uuid=uuid, pathname=pathname, 
            entities=entities, order_method=order_method, **kwargs)

        # Only load from the file system if we don't have anything.
        if self.pathname and load_yaml_files and not entities:
            self.load_entities_from_yaml_files()

        # Tell all the entities to replace their pointers with objects.
        self.replace_pointers_with_objects()

        self.find_me()


    def append(self, e):
        """
        Do a regular append and some other stuff too.
        """

        super(Project, self).append(e, self.rerun_sort_after_append)

        # Make sure the entity remembers this project.
        e.project = self


    def load_entities_from_yaml_files(self, pathname=None):
        """
        Loads all the files matching pathglob into this project.
        """

        if pathname:
            self.pathname = pathname

        if not self.pathname:
            raise ValueError("I need a path to the files!")

        if not os.path.isdir(self.pathname):
            raise ValueError("%s isn't a directory." % self.pathname)

        pathglob = os.path.join(self.pathname, '*.yaml')

        self.rerun_sort_after_append = False
        for fp in glob.glob(pathglob):

            bn = os.path.basename(fp)

            # Skip a few files.
            if bn == 'project.yaml' \
            or bn.startswith(self.__class__.__name__.lower()) \
            or bn == 'me.yaml' \
            or bn.startswith('simpleproject'):

                continue

            # Extract the class name and then look it up
            classname, dash, remainder = bn.partition('-')
            C = self.classes[classname]
            C.from_yaml_file(fp, self)

        self.rerun_sort_after_append = True
        return self


    def save_entities_to_yaml_files(self, pathname=None):
        """
        Ask every entity to write itself out to YAML.
        Returns those entities that really wrote themselves out.
        """

        if pathname is None and self.pathname is None:
            raise ValueError("I need a pathname!")

        if self.pathname is None and pathname is not None:
            self.pathname = pathname

        if not os.path.isdir(self.pathname):
            raise ValueError("%s is not a directory!")

        pathname = pathname or self.pathname

        updated_yaml_files = \
        [e for e in self if e.to_yaml_file(self.pathname)]

        self.to_pickle()

        return updated_yaml_files


    @property
    def yaml(self):
        """
        Return a block of yaml.
        """

        data = dict(
            module=self.__module__,
            classname=self.__class__.__name__,
            title=self.title,
            order_method_name=self.order_method.func_name,
            uuid=self.uuid,
        )

        return yaml.dump(data, default_flow_style=False)


    def to_yaml_file(self, pathname=None):
        """
        Save this project to a YAML file.
        """

        if not pathname \
        and (self.pathname is None or not os.path.isdir(self.pathname)):

            raise ValueError("I need a pathname!")

        pathname = pathname or self.pathname
        fp = os.path.join(pathname, 'project.yaml')
        f = open(fp, 'w')
        f.write(self.yaml)
        f.close()

        self.to_pickle(pathname)

        return fp


    def to_pickle(self, pathname=None):
        """
        Save a pickled version of this project at pathname +
        project.pickle.
        """

        if not pathname \
        and (
            self.pathname is None
            or not os.path.isdir(self.pathname)):

            raise ValueError("I need a pathname!")

        pathname = pathname or self.pathname

        pf = os.path.join(pathname, 'project.pickle')
        pickle.dump(self, open(pf, 'w'))
        return pf


    @classmethod
    def from_pickle(cls, pf):
        """
        Load a project from pickle file pf.
        """

        p = pickle.load(open(pf))
        for e in p:
            p.append(e)

        p.loaded_from = 'pickle'
        return p
    

    @classmethod
    def find_file(cls, filename='project.yaml', walkdown=False):
        """
        Raise an exception or return the path to the file filename.

        Check the os.environ first and then walk up the filesystem, then
        walk down the filesystem IFF walkdown is True.

        By the way, walking down can take a REALLY long time if you're
        at the top of a big file system.
        """

        yamlpath = os.path.join(os.environ.get('PITZDIR', ''), filename)

        if os.path.isfile(yamlpath):
            return yamlpath
        
        starting_path = os.getcwd()

        # Walk up...
        for dir in clepy.walkup(starting_path):

            a = os.path.join(dir, 'pitzdir', filename)

            if os.path.isfile(a):
                return a

        # Walk down...
        if walkdown:
            for root, dirs, files in os.walk(starting_path):

                if 'pitzdir' in dirs:
                    a = os.path.join(dir, 'pitzdir', filename)

                if os.path.isfile(a):
                    return a

        raise ProjectNotFound("Started looking at %s" % starting_path)


    @classmethod
    def find_pitzdir(cls, pitzdir=None, walkdown=False):

        """
        Return the path to the pitzdir.

        Check the pitzdir parameter first, then look in os.environ, then
        go up the directory from where we are now, and then maybe
        (depending on walkdown) go down the directory tree.

        Raises ProjectNotFound if no project could be found.
        """

        # Check parameter.
        if pitzdir:
            
            if os.path.isdir(pitzdir):
                return os.path.abspath(pitzdir)

            else:
                raise IOError("%s ain't real" % pitzdir)


        # Check os.environ['PITZDIR']
        if 'PITZDIR' in os.environ \
        and os.path.isdir(os.environ['PITZDIR']):

            return os.path.abspath(os.environ['PITZDIR'])


        # Walk up the file system.
        starting_path = os.getcwd()

        # Walk up...
        for dir in clepy.walkup(starting_path):

            p = os.path.join(dir, 'pitzdir')

            if os.path.isdir(p):
                return os.path.abspath(p)


        # Walk down...
        if walkdown:
            for root, dirs, files in os.walk(starting_path):

                if 'pitzdir' in dirs:
                    return os.path.abspath(
                        os.path.join(dir, 'pitzdir'))

        raise ProjectNotFound("Started looking at %s" % starting_path)

        # Maybe walk down the filesystem.

 
    @classmethod
    def from_pitzdir(cls, pitzdir):

        """
        Return a project (or subclass) instance based on data in
        pitzdir.  
        """

        # If we have a project.pickle, compare the timestamp of the
        # pickle to the timestamps of all the yaml files.
        pickle_path = os.path.join(pitzdir, 'project.pickle')
        if os.path.isfile(pickle_path):

            pickle_timestamp = os.stat(pickle_path).st_mtime
            
            newest_yaml = max([os.stat(f).st_mtime 
                for f in glob.glob(os.path.join(pitzdir, '*.yaml'))])

            if pickle_timestamp >= newest_yaml:
                return cls.from_pickle(pickle_path)

        yaml_path = os.path.join(pitzdir, 'project.yaml')
        if os.path.isfile(yaml_path):

            return cls.from_yaml_file(yaml_path)


        raise ProjectNotFound("Couldn't find anything in pitzdir %s"
            % pitzdir)


    @property
    def html_filename(self):

        return "index.html"

    @classmethod
    def from_yaml_file(cls, fp):
        """
        Instantiate the class based on the data in file fp.

        IMPORTANT: this may not return an instance of this project.
        Instead it will return an instance of the subclass specified in
        the yaml data.
        """

        yamldata = yaml.load(open(fp))

        # Read the section on __import__ at
        # http://docs.python.org/library/functions.html
        # to make sense out of this.
        m = __import__(yamldata['module'],
            fromlist=yamldata['classname'])

        yamldata['pathname'] = os.path.realpath(os.path.dirname(fp))

        # Dig out the string that points to the order method and replace
        # it with the actual function.  This is really ugly, so feel
        # free to fix it.
        yamldata['order_method'] = globals()[yamldata['order_method_name']]
        yamldata.pop('order_method_name')

        # This big P is the class of the project.
        P = getattr(m, yamldata['classname'])

        p = P(**yamldata)
        p.loaded_from = 'yaml'
        return p




    @property
    def todo(self):

        b = self(type='task')\
        .does_not_match_dict(status=Status(title='finished'))\
        .does_not_match_dict(status=Status(title='abandoned'))

        b.title = '%s: stuff to do' % self.title
        b._html_filename = 'todo.html'

        return b


    # TODO: replace all these properties with some metaclass tomfoolery.
    @property
    def milestones(self):
        b = self(type='milestone')
        b.title = 'Milestones'

        return b


    @property
    def components(self):
        b = self(type='component')
        b.title = 'Components'
        return b


    @property
    def tasks(self):
        b = self(type='task')
        b.title = 'Tasks'
        return b


    @property
    def people(self):
        b = self(type='person')
        b.title = 'People'
        return b


    @property
    def comments(self):
        b = self(type='comment')
        b.title = 'Comments'
        return b


    @property
    def estimates(self):
        b = self(type='estimate')
        b.title = 'Estimates'
        return b


    @property
    def statuses(self):
        b = self(type='status')
        b.title = 'Statuses'
        return b


    @property
    def unscheduled(self):
        """
        Unfinished tasks not linked to any milestones.
        """

        b = self(type='task').does_not_match_dict(status='finished')

        for m in self.milestones:
            b = b.does_not_match_dict(milestone=m)

        b.title = 'Unscheduled and unfinished tasks'
        return b


    @property
    def started(self):
        b = self(type='task', status='started')
        b.title = 'Started tasks'
        return b


    @property
    def me(self):
        return getattr(self, 'current_user', None)


    def find_me(self):

        """
        Return the person currently using this pitz session by reading
        the pitzdir/you.yaml file.
        """


        # When no people have been created, there's no point.
        if not self.people:
            return

        if hasattr(self, 'current_user'):
            return self.current_user

        pitzdir = self.pathname
        me_yaml = os.path.join(pitzdir, 'me.yaml')

        if not os.path.isfile(me_yaml):
            return
        
        self.current_user = self[yaml.load(open(me_yaml))]
        return self.current_user
