# vim: set expandtab ts=4 sw=4 filetype=python:

import glob
import logging
import os
import cPickle as pickle

import yaml
import clepy

from pitz.bag import Bag
import pitz
from pitz import by_pscore_and_milestone

from pitz import entity

log = logging.getLogger('pitz.project')


class Project(Bag):
    """
    The project keeps references to every entity.
    """

    # These are all the classes that I will try to instantiate when
    # reading yaml files.
    classes = dict(
        activity=entity.Activity,
        comment=entity.Comment,
        component=entity.Component,
        entity=entity.Entity,
        estimate=entity.Estimate,
        milestone=entity.Milestone,
        person=entity.Person,
        status=entity.Status,
        tag=entity.Tag,
        task=entity.Task,
    )

    plural_names = dict(
        [(c.plural_name, c) for c in classes.values()])

    def __init__(self, title='', uuid=None, pathname=None, entities=(),
        order_method=pitz.by_pscore_and_milestone, load_yaml_files=True,
        **kwargs):

        self.rerun_sort_after_append = True

        super(Project, self).__init__(title, uuid=uuid,
            pathname=pathname, entities=entities,
            order_method=order_method, **kwargs)

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

        if updated_yaml_files:
            pitz.run_hook(
                self.pitzdir,
                'after_saving_entities_to_yaml_files')

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

    def setup_defaults(self):

        for cls in self.classes.values():
            if hasattr(cls, 'setup_defaults'):
                cls.setup_defaults(self)

    @classmethod
    def from_pickle(cls, pf):
        """
        Load a project from pickle file pf.

        """

        p = pickle.load(open(pf))
        for e in p:
            p.append(e)

        p.loaded_from = 'pickle'
        p._shell_mode = False
        return p

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
                        os.path.join(root, 'pitzdir'))

        raise pitz.ProjectNotFound("Started looking at %s" % starting_path)

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

        raise pitz.ProjectNotFound("Couldn't find anything in pitzdir %s"
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

        b = (
            self(type='task')
            .does_not_match_dict(status=entity.Status(title='finished'))
            .does_not_match_dict(status=entity.Status(title='abandoned')))

        b.title = '%s: stuff to do' % self.title
        b._html_filename = 'todo.html'

        return b

    @property
    def recent_activity(self):
        return Bag("Recent activity", entities=self.activities[:10],
            order_method=pitz.by_descending_created_time)

    # TODO: replace all these properties with some metaclass tomfoolery.
    @property
    def activities(self):
        b = self(type='activity')
        b.title = "Activities"
        b.order(pitz.by_descending_created_time)
        return b

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
