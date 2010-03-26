# vim: set expandtab ts=4 sw=4 filetype=python:

import os

import yaml

import pitz
from pitz.entity import Entity


class Person(Entity):
    """
    Track who is doing what.
    """

    plural_name = "people"

    def save_as_me_yaml(self):
        """
        Designate this person is me by saving a me.yaml file.
        """

        if not self.project:
            raise pitz.NoProject("Sorry, saving a me.yaml needs a project")

        me_yaml_path = os.path.join(self.project.pathname, 'me.yaml')
        me_yaml = open(me_yaml_path, 'w')
        me_yaml.write(yaml.dump(self.uuid))

        return me_yaml_path

    @property
    def my_todo(self):

        if not self.project:
            return

        b = self.project.todo(owner=self)
        b.title = "To-do list for %(title)s" % self
        return b

    def __str__(self):
        return getattr(self, 'abbr', self.title)

    @classmethod
    def setup_defaults(cls, proj):
        cls(proj, title='no owner', pscore=-100)

