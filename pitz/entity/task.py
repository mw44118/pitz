# vim: set expandtab ts=4 sw=4 filetype=python:

import textwrap

import clepy

from pitz.entity import (
    Component, Entity, Estimate, Person,
    Milestone, Status, Tag, Comment,
    )

import pitz


class Task(Entity):

    plural_name = "tasks"

    cli_detailed_view_template = 'task_detailed_view.txt'
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
    def title_view(self):
        return '%-62s' % clepy.maybe_add_ellipses(self.title, 59)

    def underline_title_and_frag(self, char='-'):
        return char * (len(self.title_view) + 7)

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
    def tags(self):

        if 'tags' not in self:
            self['tags'] = self.required_fields['tags'](self.project)
        return self['tags']

    @property
    def tags_view(self):

        if self['tags']:
            return ', '.join([t.title for t in self.tags])

        else:
            return 'no tags'

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

        t = textwrap.dedent("""
            %(owner_title)s_ | %(status_title)s_ | %(estimate_title)s_ | %(milestone_title)s_ | %(pscore)s

            .. _%(owner_title)s: Person/by_title/%(owner_title)s
            .. _%(status_title)s: Status/by_title/%(status_title)s
            .. _%(estimate_title)s: Estimate/by_title/%(estimate_title)s
            .. _%(milestone_title)s: Milestone/by_title/%(milestone_title)s
        """)

        d = dict(
            owner_title=self.owner.title,
            status_title=self.status.title,
            estimate_title=self.estimate.title,
            milestone_title=self.milestone.title,
            pscore=self.pscore
        )

        return t % d


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
                    "pause those before starting this one."
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
