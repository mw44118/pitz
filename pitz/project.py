# vim: set expandtab ts=4 sw=4 filetype=python:

import glob, logging, os, pickle

import yaml

from clepy import walkup

from pitz.bag import Bag
from pitz.entity import Entity
from pitz import *

log = logging.getLogger('pitz.project')


class Project(Bag):

    """
    The project is the bag that everybody should track, because it is
    the only thing that keeps references to every other thing.
    """

    # These are all the classes that I will try to instantiate when
    # reading yaml files.
    classes = dict(
        entity = Entity
    )


    def __init__(self, title='', uuid=None, pathname=None, entities=(),
        order_method=by_pscore_and_milestone, load_yaml_files=True,
        **kwargs):

        self.rerun_sort_after_append = True

        super(Project, self).__init__(title, uuid, pathname, entities,
            order_method, **kwargs)

        # Only load from the file system if we don't have anything.
        if self.pathname and load_yaml_files and not entities:
            self.load_entities_from_yaml_files()

        # Tell all the entities to replace their pointers with objects.
        self.replace_pointers_with_objects()


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

            # Skip the project yaml file.
            if bn == 'project.yaml' \
            or bn.startswith(self.__class__.__name__.lower()):

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
        return [e for e in self if e.to_yaml_file(self.pathname)]


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
        for dir in walkup(starting_path):

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
        for dir in walkup(starting_path):

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
