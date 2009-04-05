# vim: set expandtab ts=4 sw=4 filetype=python:

import jinja2

from pitz.entity import Entity

class Task(Entity):

    required_fields = dict(
        title='no title',
        status='unknown status')

    pointers = ['milestone', 'person', 'component']

    @property
    def summarized_view(self):
        """
        Short description of the task.
        """

        return "%(title)s (%(status)s)" % self
