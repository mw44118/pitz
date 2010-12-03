# vim: set expandtab ts=4 sw=4 filetype=python:

import unittest

import mock

from pitz.webapp import handlers
from pitz.project import Project

class TestTeam1(unittest.TestCase):

    def test_instantiate(self):
        handlers.Team(mock.Mock())

class TestTeam2(unittest.TestCase):

    def setUp(self):

        proj = Project(title='Project used in TestTeam2')
        self.th = handlers.Team(proj)

    def test_wants_to_handle(self):

        assert self.th.wants_to_handle({'PATH_INFO':'/team'})

    def test_call(self):

        bogus_start_response = mock.Mock()
        self.th({}, bogus_start_response)

        self.assertTrue(bogus_start_response.called)

        self.assertEqual(
            bogus_start_response.call_args[0][0],
            '200 OK',
            bogus_start_response.call_args[0][0])
