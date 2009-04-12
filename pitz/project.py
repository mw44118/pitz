# vim: set expandtab ts=4 sw=4 filetype=python:

import glob, os

from pitz.bag import Bag
import pitz.entity


class Project(Bag):

    """
    The project is the bag that everybody should track, because it is
    the only thing that keeps references to every other thing.
    """

    # These are all the standard classes.
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

        if not pathname \
        and not self.pathname \
        and not os.path.isdir(self.pathname):
            raise ValueError("I need a pathname!")

        pathname = pathname or self.pathname

        # Send all the entities to the filesystem.
        return [e.to_yaml_file(pathname) 
            for e in self.entities]
