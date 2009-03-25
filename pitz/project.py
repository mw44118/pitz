# vim: set expandtab ts=4 sw=4 filetype=python:

from pitz.bag import Bag

class Project(Bag):

    """
    The project is the bag that everybody should track.
    """
    
    # TODO: Use some metaclass nonsense to automate creation
    # of all these properties.

    @property
    def tasks(self):
        return self.matches_dict(type='task')

    @property
    def milestones(self):
        return self.matches_dict(type='milestone')

    @property
    def people(self):
        return self.matches_dict(type='person')

    @property
    def components(self):
        return self.matches_dict(type='component')

    # End of stuff to somehow figure out dynamically.

    @property
    def summarized_view(self):

        s = "<pitz.Project '%s' (%d tasks, %d milestones, %d people, %d components)>"

        return s % (
            self.title,
            len(self.tasks),
            len(self.milestones),
            len(self.people),
            len(self.components))


    def append(self, e):
        """
        Link an entity to this project.
        """

        super(Project, self).append(e)
        e.project = self
