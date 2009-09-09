# vim: set expandtab ts=4 sw=4 filetype=python:

"""
Verify we can use pitz for an agile workflow, where "agile" means:

* one project has many releases.
* each release has one or more iterations.
* each iteration has numerous user stories.
* each story has numerous tasks.
"""

import unittest
from nose.tools import raises

from pitz.agilepitz import *


class TestAgile(unittest.TestCase):


    def setUp(self):

        self.ap = AgileProject()
     
        self.ap.append(UserStory(
            self.ap,
            title='Draw new accounting report',
            priority=Priority(self.ap, level=2, title="two")))

        self.ap.append(UserStory(
            self.ap,
            title='Improve speed of search page',
            priority=Priority(self.ap, level=1, title="one")))

        self.ap.append(UserStory(
            self.ap,
            title='Add animation to site logo',
            estimate=Estimate(self.ap, title="straightforward",
            points=2)))

        self.ap.append(UserStory(
            self.ap,
            title='Write "forgot password?" feature',
            priority=Priority(self.ap, level=1, title="one"),
            estimate=Estimate(self.ap, title="straightforward",
            points=2)))

        self.ap.append(UserStory(
            self.ap,
            title='Allow customer to change contact information',
            priority=Priority(level=1, title="one"),
            estimate=Estimate(self.ap, title="straightforward", points=2)))

        self.ap.append(UserStory(
            self.ap,
            title='Allow customer to change display name',
            priority=Priority(self.ap, level=1, title="one"),
            estimate=Estimate(self.ap, title="easy", points=1)))

        # Reset all the stories.
        for us in self.ap.stories:
            us.send_to_backlog()


    def test_show_backlog_1(self):
        """
        List every user story in the backlog, ordered by priority.
        """

        assert len(self.ap.backlog) == 6, len(self.ap.backlog)


    def test_show_backlog_2(self):
        """
        Only list the estimated stories in the backlog, ordered by priority.
        """

        assert len(self.ap.estimated_backlog) == 4, len(self.ap.estimated_backlog)


    def test_show_backlog_3(self):
        """
        Only list unestimated stories in the backlog, ordered by priority.
        """

        b = self.ap.backlog(
            estimate=Estimate(self.ap, title='not estimated',
            points=None))

        assert len(b) == 2, len(b)
        assert b[0]['priority'] <= b[1]['priority']


    def test_estimate_story_1(self):

        """
        Create tasks for a story and then add an estimate to the story.
        """

        us = self.ap.backlog(estimate=Estimate(self.ap,
            title='not estimated', points=None))[0]

        assert us in self.ap.backlog(
            estimate=Estimate(
                self.ap, title='not estimated', points=None))

        self.ap.append(Task(self.ap, title="Get mockups approved", story=us))
        self.ap.append(Task(self.ap, title="Write queries", story=us))
        self.ap.append(Task(self.ap, title="Write some tests", story=us))
        us['estimate'] = Estimate(self.ap, title='easy', points=1)

        assert us not in self.ap.backlog(estimate=Estimate(title='not estimated', points=None))


    def test_add_story_1(self):

        """
        Add a single story to an iteration.
        """

        not_estimated = Estimate(self.ap, title='not estimated',
            points=None)

        print("not estimated frag: %s" % not_estimated.frag)

        self.ap.order()
        it99 = Iteration(self.ap, title="Iteration for week 99", velocity=5)

        print("%d stories total in project"
            % (self.ap(type='userstory').length))

        for us in self.ap(type='userstory'):
            print("%(title)s: %(status)s %(estimate)s" % us)
            print(us['estimate'].frag)

        print("self.ap.estimated_backlog.length is %d"
            % self.ap.estimated_backlog.length)

        s = self.ap.estimated_backlog[0]

        print("title of estimated story is %s" % s.title)
        print("status frag of estimated story is %s" 
            % s['estimate'].frag)

        assert s['status'] == Status(self.ap, title='backlog'), \
        "status for %(title)s is %(status)s!" % s

        it99.add_story(s)

        assert s['status'] == Status(self.ap, title='planned'), \
        "status for %(title)s is %(status)s!" % s
        
        assert len(it99.stories) == 1
        assert len(it99.stories) == 1

        assert it99.stories[0] == s

        assert it99.points == s.points, '%s != %s' % (it99.points, s.points)

        assert it99.slack == it99.velocity - s.points


    def test_plan_iteration_1(self):
        """
        Figure out what user stories can fit into the next release.
        """

        self.ap.order()

        it99 = Iteration(self.ap, title="Iteration for week 99",
            velocity=5)

        print("it99 has %d points of slack." % it99.slack)

        print("ap has %d stories in the estimated backlog." 
            % self.ap.estimated_backlog.length)

        assert it99.stories.length == 0, it99.stories.length
        it99.plan_iteration()

        print("it99 has %d stories" % it99.stories.length)

        assert it99.points == it99['velocity'], \
        "%s != %s" % (it99.points, it99['velocity'])

        assert not it99.slack, it99.slack

        for s in it99.stories:
            print(s.summarized_view)
            assert s['iteration'] == it99
            assert s['status'] == Status(title='planned'), s['status']
        

    def test_plan_iteration_2(self):
        """
        Plan the next two iterations.
        """

        self.ap.order()
        it99 = Iteration(self.ap, title="Iteration for week 99", velocity=5)
        it99.plan_iteration()

        print("stories in it99")
        for s in it99.stories:
            print(s.summarized_view)
            print(s.points)

        assert len(it99.stories) == 3

        it100 = Iteration(self.ap, title="Iteration for week 100", velocity=5)
        it100.plan_iteration()

        print("stories in it100")
        for s in it100.stories:
            print(s.summarized_view)
            print(s.points)
        assert len(it100.stories) == 1, len(it100.stories)


    def test_plan_iteration_3(self):

        """
        Take something out of an iteration in order to make room for
        something else.
        """

        self.ap.order()

        it99 = Iteration(self.ap, title="Iteration for week 99", velocity=5)

        it99.plan_iteration()

        assert it99.points == it99['velocity']
        assert not it99.slack

        s1, s2, s3 = it99.stories
        s2.send_to_backlog()

        assert it99.slack, "it99.slack is %s" % it99.slack


    @raises(Exception)
    def test_add_story_2(self):

        """
        Try to add another story after using up the slack.
        """

        self.ap.order()

        it99 = Iteration(self.ap, title="Iteration for week 99",
            velocity=5)

        it99.plan_iteration()

        assert it99.points == it99['velocity']

        assert not it99.slack, \
        "it99 has %d slack remaining!" % it99.slack

        it99.add_story(UserStory(ap,
            title="Bogus extra story", estimate=3))


    def test_finished_points(self):

        it99 = Iteration(self.ap,
            title="Iteration for week 99", velocity=5)

        it99.finished_points
