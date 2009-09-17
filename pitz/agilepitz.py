# vim: set expandtab ts=4 sw=4 filetype=python:

"""\
Agile: releases, iterations, stories, tasks, and velocity.
"""

myclassname = 'AgileProject'

import pitz
import pitz.project
import pitz.entity

from pitz.simplepitz import *

class Release(pitz.entity.Entity):
    pass

class Iteration(pitz.entity.Entity):

    required_fields = dict(
        title='Untitled iteration',
        description='',
        pscore=0,
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

        return self.velocity - self.points_planned

        
    @property
    def points_planned(self):
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


class UserStory(pitz.entity.Entity):

    required_fields = dict(
        title=None,
        description='',
        pscore=0,
        points=0,
        status=Status(title="backlog"),
        estimate=Estimate(title='not estimated', points=None),
    )

    allowed_types = dict(
        status=Status,
        estimate=Estimate,
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
        status=Status,
        estimate=Estimate,
        task=Task,
        person=Person,
        milestone=Milestone,
        comment=Comment,
        component=Component,
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

        return backlog


    @property
    def estimated_backlog(self):
        """
        Returns a bag holding estimated stories.
        """
        
        self.order()

        backlog = self(
            type='userstory',
            status=Status(self, title='backlog'))\
        .does_not_match_dict(
            estimate=Estimate(self, title='not estimated'))

        backlog.title = 'Estimated stories in backlog'


        return backlog
