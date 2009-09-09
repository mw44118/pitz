# vim: set expandtab ts=4 sw=4 filetype=python:

"""\
Agile: releases, iterations, stories, tasks, and velocity.

WARNING!!!
This one isn't as well developed as the simple project.  Once I
finish that one, I'll work on this one.
"""

myclassname = 'AgileProject'

import pitz
import pitz.project
import pitz.entity

from pitz.simplepitz import Task, Estimate, Status, \
SimpleProject

class Release(pitz.entity.Entity):
    pass

class Iteration(pitz.entity.Entity):

    required_fields = dict(
        title='Untitled iteration',
        velocity=10,
    )

    @property
    def stories(self):

        """
        Return a bag of all this iteration's stories.
        """

        stories = self.project(type='userstory', iteration=self)
        stories.title = self['title']

        return stories

    @property
    def velocity(self):
        return self['velocity']

    @property
    def slack(self):
        """
        Return the difference between velocity and the sum of all
        planned stories.
        """

        return self.velocity - self.points

        
    @property
    def points(self):
        """
        Return the sum of points for all stories in this iteration.
        """

        return sum([s.points for s in self.stories 
            if s.points is not None])
        

    @property
    def finished_points(self):
        """
        Return the sum of points for all completed stories.
        """

        return sum([s['estimate'] for s in self.stories if s['status'] == 'finished'])


    def plan_iteration(self):
        """
        Assign enough stories from the backlog to fill up this
        iteration.
        """

        for story in self.project.estimated_backlog:

            # Only add the story if it will fit.
            if self.slack >= story.points:
                self.add_story(story)


    def add_story(self, story):

        """
        Check the slack and then maybe add a story.
        """

        if self.slack >= story['estimate']['points']:
            story['status'] = Status(self.project, title='planned')
            story['iteration'] = self

        else:
            raise Exception("Not enough slack for this story!")


class Priority(pitz.entity.Entity):
    """
    Tracks importance.
    """

class UserStory(pitz.entity.Entity):

    required_fields = dict(
        title=None,
        priority=Priority(level=5, title="Critical"),
        status=Status(title="backlog"),
        estimate=Estimate(title='not estimated', points=None),
    )

    allowed_types = dict(
        status=Status,
        estimate=Estimate,
        priority=Priority,
    )


    @property
    def points(self):
        return self['estimate']['points']

    def send_to_backlog(self):
        """
        Pull this story out of any iterations and put it back in the
        backlog.
        """

        self['status'] = Status(self.project, title='backlog')
        if 'iteration' in self:
            self.pop('iteration')


class AgileProject(SimpleProject):

    classes = dict(
        release=Release,
        iteration=Iteration,
        userstory=UserStory,
    )

    @property
    def stories(self):
        b = self(type='userstory')
        b.title = 'stories'
        return b


    @property
    def backlog(self):

        self.order()

        backlog = self(type='userstory',
            status=Status(title='backlog'))

        backlog.title = 'All stories in backlog'

        backlog.order_method = pitz.by_whatever('by_priority',
            'priority')

        return backlog

    @property
    def estimated_backlog(self):
        """
        Returns a bag holding stories with any estimate but not 'not
        estimated'.
        """
        
        self.order()

        backlog = self(
            type='userstory',
            status=Status(self, title='backlog'))\
        .does_not_match_dict(
            estimate=Estimate(self, title='not estimated', points=None))

        backlog.title = 'Estimated stories in backlog'
        backlog.order_method = pitz.by_whatever('by_priority', 'priority')

        return backlog
