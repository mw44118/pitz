# vim: set expandtab ts=4 sw=4 filetype=python:

import pitz
import pitz.project
import pitz.entity

class Release(pitz.entity.Entity):
    pass

class Iteration(pitz.entity.Entity):

    pointers = ['release']

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
    def slack(self):
        """
        Return the difference between velocity and the sum of all
        planned stories.
        """

        return self['velocity'] - self.points

        
    @property
    def points(self):
        """
        Return the sum of points for all stories in this iteration.
        """

        return sum([s['estimate'] for s in self.stories])
        

    def plan_iteration(self):
        """
        Assign enough stories from the backlog to fill up this
        iteration.
        """

        points_used = 0
        
        for story in self.project.estimated_backlog:

            # Only add the story if it will fit.
            if self['velocity'] >= points_used + story['estimate']:
                self.add_story(story)
                points_used += story['estimate']

    def add_story(self, story):

        """
        Check the slack and then maybe add a story.
        """

        if self.slack >= story['estimate']:
            story['status'] = 'planned'
            story['iteration'] = self

        else:
            raise Exception("Not enough slack for this story!")
        

class UserStory(pitz.entity.Entity):

    required_fields = dict(
        title=None,
        priority=5,
        status='backlog',
        estimate='unknown',
    )

    allowed_values = dict(
        status=['backlog', 'planned', 'started', 'stopped', 'finished'],
        estimate=set(['unknown', 1, 2, 3]),
        priority=range(0, 6),
    )

    pointers = ['iteration']


    def send_to_backlog(self):
        """
        Pull this story out of any iterations and put it back in the
        backlog.
        """

        self['status'] = 'backlog'
        self.pop('iteration')


class Task(pitz.entity.Entity):

    pointers = ['story']


class AgileProject(pitz.project.Project):

    classes = dict(
        release=Release,
        iteration=Iteration,
        userstory=UserStory,
    )

    @property
    def backlog(self):

        self.order()

        backlog = self(type='userstory', status='backlog')
        backlog.title = 'All stories in backlog'
        backlog.order_method = pitz.by_whatever('by_priority', 'priority')

        return backlog

    @property
    def estimated_backlog(self):
        
        self.order()

        backlog = self(type='userstory', status='backlog')\
        .does_not_match_dict(estimate='unknown')

        backlog.title = 'Estimated stories in backlog'
        backlog.order_method = pitz.by_whatever('by_priority', 'priority')

        return backlog
