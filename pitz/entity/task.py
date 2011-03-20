# vim: set expandtab ts=4 sw=4 filetype=python:

import logging
import textwrap

import clepy
import jinja2

from pitz.entity import (
    Component, Entity, Estimate, Person,
    Milestone, Status, Tag, Comment,
    )

import pitz

log = logging.getLogger('entity.task')

class Task(Entity):

    plural_name = "tasks"

    cli_detailed_view_template = 'task_detailed_view.txt'
    rst_detailed_view_template = 'task_rst_detailed_view.txt'
    colorized_detailed_view_template = 'colorized_task_detailed_view.txt'
    cli_verbose_view_template = 'task_verbose_view.txt'

    allowed_types = dict(
        owner=Person,
        points=int,
        milestone=Milestone,
        status=Status,
        estimate=Estimate,
        components=[Component],
        tags=[Tag])

    required_fields = dict(
        title=None,
        description='',
        pscore=0,
        owner=lambda proj: Person(proj, title="no owner"),
        milestone=lambda proj: Milestone(proj, title='unscheduled'),
        status=lambda proj: Status(proj, title='unstarted'),
        estimate=lambda proj: Estimate(proj, title='not estimated'),
        components=lambda proj: list(),
        tags=lambda proj: list(),
    )

    jinja_template = 'task.html'

    def __init__(self, project=None, **kwargs):
        super(Task, self).__init__(project, **kwargs)

    @property
    def title_color(self):
        """
        Return the color to use for the title
        """

        status_title_colors = dict(
            finished='dark_green',
            started='green',
            paused='yellow',
            queued='white',
            unstarted='white',
            abandoned='gray',
        )

        return pitz.colors[status_title_colors[self.status.title]]

    @property
    def colorized_title_view(self):
        """
        Return the title string dressed up in a bash color.
        """

        return '%s%-62s%s' % (
            self.title_color,
            clepy.maybe_add_ellipses(self.title, 59),
            pitz.colors['clear'])

    @property
    def colorized_title_view_without_ellipses(self):
        """
        Return the title string dressed up in a bash color.
        """

        return '%s%-62s%s' % (
            self.title_color,
            self.title,
            pitz.colors['clear'])


    @property
    def milestone(self):
        return self['milestone']

    @property
    def status(self):
        return self['status']

    @property
    def estimate(self):
        return self['estimate']

    @property
    def html_summarized_view(self):

        return "%s (%s)""" % (
            super(Task, self).html_summarized_view,
            self['status'].html_summarized_view)

    @property
    def html(self):

        tmpl = self.e.get_template(self.jinja_template)
        return tmpl.render(task=self)

    @property
    def colorized_summarized_view(self):

        return self.e.get_template('colorized_task_summarized_view.txt')\
        .render(e=self)

    @property
    def summarized_view(self):
        """
        Short description of the task.
        """

        return self.e.get_template('task_summarized_view.txt')\
        .render(e=self)

    @property
    def rst_summarized_view(self):

        return self.e.get_template('task_rst_summarized_view.txt')\
        .render(e=self)

    @property
    def comments_view(self):

        return self.e.get_template(
            'task_comments_view.txt').render(e=self)

    @property
    def owner(self):
        return self.get('owner', 'no owner')

    @property
    def components(self):
        return self['components']

    @property
    def components_view(self):
        """
        Return a string (maybe empty) of this task's components.
        """

        if self['components']:
            return ', '.join(c.title for c in self.components)

        else:
            return 'no components'

    @property
    def tags(self):

        if 'tags' not in self:
            self['tags'] = self.required_fields['tags'](self.project)
        return self['tags']


    @property
    def tags_view(self):

        """
        Return a string like:

            web, tests, documentation, data model, CLI

        made from this task's tags.
        """

        if self.tags:
            return ', '.join(tag.title for tag in self.tags)

        else:
            return 'no tags'

    @property
    def rst_tags_view(self):

        """
        Returns a string like:

            `web`_, `tests`_, `documentation`-, `data model`_, `CLI`_

            .. _`web`: Tag/by_title/web
            .. _`tests`: Tag/by_title/tests
            .. _`documentation`: Tag/by_title/documentation
            .. _`data model`: Tag/by_title/data model
            .. _`CLI`: Tag/by_title/CLI
        """

        if self.tags:

            first_row = ', '.join(['`%(title)s`_' % tag
                for tag in self.tags])

            log.debug('first_row is %s' % first_row)

            targets = '\n'.join([
                tag.rst_link_target_view for tag in self.tags])

            return """%(first_row)s\n\n%(targets)s\n\n""" \
                % dict(first_row=first_row, targets=targets)

        else:
            return 'no tags'


    @property
    def interesting_attributes_view(self):
        """
        Return a string like:

            owner | status | estimate | milestone | pscore

        using this task's values for those attributes
        """

        return ' | '.join([str(s) for s in (
            self.owner,
            self.status,
            self.estimate,
            self.milestone,
            self.pscore,
        )])

    @property
    def rst_interesting_attributes_view(self):
        """
        Return a string like:

            matt_ | started_ | straightforward_ | 1.0_ | 0

            .. _matt: Person/by_title/matt
            .. _started: Status/by_title/started
            .. _straightforward: Estimate/by_title/straightforward
            .. _1.0: Milestone/by_title/1.0

        using this task's values for those attributes.
        """

        t = jinja2.Template(textwrap.dedent("""
            `{{t.owner.title}}`_ | `{{t.status.title}}`_ | `{{t.estimate.title}}`_ | `{{t.milestone.title}}`_ | {{t.pscore}}

            {{t.owner.rst_link_target_view}}
            {{t.status.rst_link_target_view}}
            {{t.estimate.rst_link_target_view}}
            {{t.milestone.rst_link_target_view}}
        """))

        return t.render(t=self)


    @property
    def colorized_one_line_view(self):
        """
        Should fit within 72 characters.
        """

        return '%s %s' % (self.colorized_title_view, self.colorized_frag)


    @property
    def one_line_view(self):
        """
        Should fit within 72 characters.
        """

        return '%s %s' % (self.title_view, self.frag)

    @property
    def recent_activity(self, how_many=5):
        """
        Return some (specified by how_many) activities.
        """

        b = self.activities[:how_many]
        b.title = 'Recent activity'

        return b

    @property
    def recent_activity_view(self):

        return self.e.get_template('task_activity_view.txt')\
        .render(activity=self.recent_activity)

    def abandon(self, comment_title=None, comment_description=None):

        if self['status'].title in ['unstarted', 'started']:

            self['status'] = Status(title='abandoned')

            if 'owner' in self:
                self.pop('owner')

            if comment_title and self.project and self.project.me:

                Comment(self.project, who_said_it=self.project.me,
                    title=comment_title,
                    entity=self,
                    description=comment_description)

            return self

        else:
            raise ValueError(
                'You can only abandon unstarted or started tasks.')


    def start(self, ignore_other_started_tasks=False):

        if self.project and self.project.me:

            other_started_tasks = self.project.tasks.matches_dict(
                owner=self.project.me,
                status='started')

            if other_started_tasks and not ignore_other_started_tasks:

                raise pitz.OtherTaskStarted(
                    "You have %d other tasks started; "
                    "pause those (with -z) before starting this one."
                    % other_started_tasks.length)

        self['status'] = Status(title='started')

        return self


    def pause(self):
        self['status'] = Status(title='paused')


    def finish(self):

        self['status'] = Status(title='finished')

        return self


    def assign(self, owner):

        self['owner'] = owner
