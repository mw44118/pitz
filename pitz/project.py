# vim: set expandtab ts=4 sw=4 filetype=python:

import glob, os

import yaml

from pitz.bag import Bag
import pitz.entity


class Project(Bag):

    """
    The project is the bag that everybody should track, because it is
    the only thing that keeps references to every other thing.
    """

    # These are all the classes that I will try to instantiate when
    # reading yaml files.
    classes = dict(
        entity = pitz.entity.Entity
    )


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
            if bn.startswith('project-'): continue

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
            name=self.name,
            pathname=self.pathname,
        )

        return yaml.dump(data, default_flow_style=False)

    def to_yaml_file(self, pathname=None):
        """
        Save this bag to a YAML file.
        """

        if not pathname \
        and (self.pathname is None or not os.path.isdir(self.pathname)):

            raise ValueError("I need a pathname!")

        pathname = pathname or self.pathname

        fp = os.path.join(pathname, '%s.yaml' % (self.name)) 
        f = open(fp, 'w')
        f.write(self.yaml)
        f.close()

        return fp

    @classmethod
    def from_yaml_file(cls, fp): 
        d = yaml.load(open(fp))

        # Dig out the string that points to the order method and replace
        # it with the actual function.  This is really ugly, so feel
        # free to fix it.
        d['order_method'] = globals()[d['order_method_name']]
        d.pop('order_method_name')

        return cls(**d)
