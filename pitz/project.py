# vim: set expandtab ts=4 sw=4 filetype=python:

import glob, os, subprocess

import yaml

from pitz.bag import Bag
from pitz.entity import Entity
from pitz import *

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
        order_method=by_created_time, load_yaml_files=True, **kwargs):

        super(Project, self).__init__(title, uuid, pathname, entities,
            order_method, **kwargs)

        # Only load from the file system if we don't have anything.
        if self.pathname and load_yaml_files and not entities:
            self.load_entities_from_yaml_files()

        # Tell all the entities to replace pointers with
        # objects.
        # TODO: 
        self.replace_pointers_with_objects()


    def append(self, e):
        """
        Do a regular append and some other stuff too.
        """

        super(Project, self).append(e)

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

        for fp in glob.glob(pathglob):

            bn = os.path.basename(fp)

            # Skip the project yaml file.
            if bn.startswith(self.__class__.__name__.lower()):

                continue

            # Extract the class name and then look it up
            classname, dash, remainder = bn.partition('-')
            C = self.classes[classname]
            C.from_yaml_file(fp, self)

        return self

    def save_entities_to_yaml_files(self, pathname=None):
        """
        Tell every entity to write itself out to YAML.
        """

        if pathname is None and self.pathname is None:
            raise ValueError("I need a pathname!")

        if self.pathname is None and pathname is not None:
            self.pathname = pathname

        if not os.path.isdir(self.pathname):
            raise ValueError("%s is not a directory!")

        pathname = pathname or self.pathname

        # Send all the entities to the filesystem.
        return [e.to_yaml_file(pathname) 
            for e in self.entities]

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
        lowered_class_name = self.__class__.__name__.lower()
        uuid = self.uuid

        fp = os.path.join(
            pathname, 
            '%(lowered_class_name)s-%(uuid)s.yaml' % locals())

        f = open(fp, 'w')
        f.write(self.yaml)
        f.close()

        return fp

    @classmethod
    def find_yaml_file(cls):
        """
        Raise an exception or return the path to the project.yaml file.
        """
        
        starting_path = os.getcwd()

        for dir in walkup(starting_path):

            a = os.path.join(dir, 'pitzfiles', 'project.yaml')

            if os.path.isfile(a):
                return a

        else:
            raise ProjectYamlNotFound("Started looking at %s" % starting_path)


    @classmethod
    def from_yaml_file(cls, fp):
        """
        Instantiate the class based on the data in file fp.
        """

        d = yaml.load(open(fp))
        d['pathname'] = os.path.realpath(os.path.dirname(fp))

        # Dig out the string that points to the order method and replace
        # it with the actual function.  This is really ugly, so feel
        # free to fix it.
        d['order_method'] = globals()[d['order_method_name']]
        d.pop('order_method_name')

        return cls(**d)

