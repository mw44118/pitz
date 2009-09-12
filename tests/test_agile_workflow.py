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
            pscore=1,
            estimate=Estimate(title='not estimated')))

        self.ap.append(UserStory(
            self.ap,
            title='Improve speed of search page',
            pscore=2,
            estimate=Estimate(title='not estimated')))

        self.ap.append(UserStory(
            self.ap,
            title='Add animation to site logo',
            pscore=3,
            estimate=Estimate(self.ap, title="straightforward",
                points=2)))

        self.ap.append(UserStory(
            self.ap,
            title='Write "forgot password?" feature',
            pscore=4,
            estimate=Estimate(self.ap, title="straightforward",
                points=2)))

        self.ap.append(UserStory(
            self.ap,
            title='Allow customer to change contact information',
            pscore=5,
            estimate=Estimate(self.ap, title="straightforward", points=2)))

        self.ap.append(UserStory(
            self.ap,
            title='Allow customer to change display name',
            pscore=6,
            estimate=Estimate(self.ap, title="easy", points=1)))

        # Reset all the stories.
        for us in self.ap.stories:
            us.send_to_backlog()


    def test_order(self):

        """
        Verify we order by milestone, status, pscore, created time.
        """
        
        self.ap.order()

        prev_story = None
        for story in self.ap.stories:

            if prev_story is None:
                continue

            assert prev_story >= story
            
            sort_keys = ['milestone', 'status', 'pscore', 'created_time']

            t1 = [prev_story[k] for k in sort_keys]
            t2 = [story[k] for k in sort_keys]

            assert t1 >= t2


    def test_show_backlog_1(self):
        """
        List every user story in the backlog.
        """

        assert len(self.ap.backlog) == 6, len(self.ap.backlog)


    def test_show_backlog_2(self):
        """
        List estimated backlog stories.
        """

        assert len(self.ap.estimated_backlog) == 4, \
        len(self.ap.estimated_backlog)


    def test_show_backlog_3(self):
        """
        List unestimated backlog stories.
        """

        b = self.ap.backlog(
            estimate=Estimate(self.ap, title='not estimated',
            points=None))

        assert len(b) == 2, len(b)


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

        assert it99.points_planned == s.points, '%s != %s' % (it99.points, s.points)

        assert it99.slack == it99.velocity - s.points


    def test_plan_iteration_1(self):
        """
        Figure out what user stories can fit into the next release.
        """

        self.ap.order()

        assert self.ap.backlog.length == self.ap.stories.length

        it99 = Iteration(self.ap, title="Iteration for week 99",
            velocity=5)

        print("it99 has %d points of slack." % it99.slack)

        print("ap has %d stories in the estimated backlog." 
            % self.ap.estimated_backlog.length)

        assert it99.stories.length == 0, it99.stories.length

        it99.plan_iteration()

        print("After planning, it99 has %d stories" % it99.stories.length)

        print("it99 now has %d points planned" % it99.points_planned)

        print("These are the next few stories in the backlog:")

        for s in self.ap.backlog[:3]:
            print "%(title)s %(pscore)s %(points)s" % s

        assert self.ap.backlog.length + it99.stories.length \
        == self.ap.stories.length


        assert it99.points_planned == it99['velocity'], \
        "%s != %s" % (it99.points_planned, it99['velocity'])

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
        assert self.ap.backlog.length == self.ap.stories.length

        it99 = Iteration(self.ap, title="Iteration for week 99", velocity=5)
        it99.plan_iteration()

        print("stories in it99")
        for s in it99.stories:
            print("%(title)s %(pscore)s %(points)s" % s)

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

        assert it99.points_planned == it99['velocity']
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


    def test_estimated_backlog(self):

        """
        Verify estimated_backlog only includes estimated stories.
        """

        assert self.ap.backlog.length == self.ap.stories.length

        print "title, pscore, estimate"

        for s in self.ap.stories:
            print("%(title)s: %(pscore)s %(estimate)s" % s)

        assert self.ap.estimated_backlog.length == 4


