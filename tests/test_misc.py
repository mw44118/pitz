# vim: set expandtab ts=4 sw=4 filetype=python:


import unittest

from pitz import by_pscore_and_milestone
from pitz.entity import Entity
from pitz.bag import Project

from mock import Mock, patch

m, t = Mock(), Mock()

class TestByPscoreAndMilestone(unittest.TestCase):

    def setUp(self):

        self.p = Project(title='test sorting...')
        Entity(self.p, title='a', pscore=2)
        Entity(self.p, title='b', pscore=1)
        Entity(self.p, title='c', pscore=3)

    def test_by_pscore_and_milestone(self):

        self.p.order(by_pscore_and_milestone)
        prevscore = 99

        for e in self.p:
            print(e)

            assert e['pscore'] < prevscore, \
            '%s, %s' % (e['pscore'], prevscore)

            prevscore = e['pscore']
