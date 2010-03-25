# vim: set expandtab ts=4 sw=4 filetype=python:

import clepy

from pitz.entity import Component, Entity, Estimate, Person, \
Milestone, Status, Tag

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
    def colorized_title(self):
        """
        Return the title string dressed up in a bash color.
        """

        return '%s%-62s%s' % (
            self.title_color,
            clepy.maybe_add_ellipses(self.title, 59),
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
    def summarized_view(self):
        """
        Short description of the task.
        """

        return self.e.get_template('task_summarized_view.txt')\
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

            owner | status | estimate | milestone

        using this task's values for those attributes
        """

        return ' | '.join([str(s) for s in (
            self.owner,
            self.status,
            self.estimate,
            self.milestone,
        )])


    @property
    def recent_activity(self, how_many=5):
        """
        Return some (specified by how_many) activities.
        """

        # Importing this here because the bag module also imports this.
        # When I fix slicing on bags, this won't be necessary.
        from pitz.bag import Bag

        recent_activities = self.activities[:how_many]
        b = Bag(
            'Recent activity',
            entities=recent_activities,
            order_method=self.activities.order_method)

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


    def start(self, comment_title=None, comment_description=None):

        self['status'] = Status(title='started')

        if comment_title and self.project and self.project.me:

            Comment(self.project, who_said_it=self.project.me,
                entity=self,
                title=comment_title,
                description=comment_description)

        return self


    def finish(self, comment_title=None, comment_description=None):

        self['status'] = Status(title='finished')

        if comment_title and self.project and self.project.me:

            Comment(self.project, who_said_it=self.project.me,
                title=comment_title,
                entity=self,
                description=comment_description)

        return self


    def assign(self, owner):

        self['owner'] = owner
