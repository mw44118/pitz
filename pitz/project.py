# vim: set expandtab ts=4 sw=4 filetype=python:

from pitz.bag import Bag

class Project(Bag):

    """
    The project is the bag that everybody should track, because it is
    the only thing that keeps references to every other thing.
    """
    
    # TODO: Use some dynamic nonsense to automate creation
    # of all these properties based on all subclasses of Entity in
    # this project.
    @property
    def tasks(self):
        b = self.matches_dict(type='task')
        b.title ='Tasks in project %s' % self.title
        return b

    @property
    def releases(self):
        return self.matches_dict(type='release')

    @property
    def iterations(self):
        return self.matches_dict(type='iteration')

    @property
    def people(self):
        return self.matches_dict(type='person')

    @property
    def components(self):
        return self.matches_dict(type='component')

    # End of stuff to somehow figure out dynamically.

    def append(self, e):
        """
        Do a regular append and also set the entity's project attribute
        to this project.
        """

        super(Project, self).append(e)
        e.project = self
