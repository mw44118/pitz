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

    jinja_template = "person.html"

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
    def html(self):
        tmpl = self.e.get_template(self.jinja_template)
        return tmpl.render(person=self)

    @property
    def my_todo(self):

        if not self.project:
            return

        b = self.project.todo(owner=self)
        b.title = "To-do list for %(title)s" % self

        b.order_method = pitz.by_whatever('xxx', 'milestone', 'status',
            'pscore', reverse=True)

        return b

    @property
    def top_priority_task(self):

        if not self.project:
            return

        return self.my_todo[0]

    def __str__(self):
        return getattr(self, 'abbr', self.title)

    @property
    def first_four_tasks(self):

        if not self.project:
            return

        first_four_tasks = self.my_todo[:4]
        first_four_tasks.title = 'First four tasks from to-do list'
        return first_four_tasks

    @property
    def use_colorization(self):
        return self.get('use_colorization', None)

    @classmethod
    def setup_defaults(cls, proj):
        cls(proj, title='no owner', pscore=-100, is_a_default=True)

    @property
    def my_activities(self):

        all_my_activities = self.project.activities(who_did_it=self)

        return all_my_activities.order(pitz.by_descending_created_time)

    @property
    def four_recent_activities(self):

        four_recent_activities = self.my_activities[:4]
        four_recent_activities.title = 'Four most recent activities'
        return four_recent_activities
