# vim: set expandtab ts=4 sw=4 filetype=python:

from pitz.bag import Bag

class Project(Bag):

    """
    The project is the bag that everybody should track, because it is
    the only thing that keeps references to every other thing.
    """

    def append(self, e):
        """
        Do a regular append and some other stuff too.
        """

        super(Project, self).append(e)

        # Make sure the entity remembers this project.
        e.project = self

