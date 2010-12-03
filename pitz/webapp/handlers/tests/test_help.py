# vim: set expandtab ts=4 sw=4 filetype=python:

import unittest
import wsgiref.util

import mock

from pitz.webapp import handlers

class TestHelpHandler(unittest.TestCase):

    def setUp(self):
        self.bogus_environ = {'PATH_INFO':'/help'}
        wsgiref.util.setup_testing_defaults(self.bogus_environ)
        self.bogus_start_response = mock.Mock()
        self.bogus_project = mock.Mock()
        self.hh = handlers.HelpHandler(self.bogus_project)

    def test_init(self):
        handlers.HelpHandler(self.bogus_project)

    def test_wants_to_handle(self):

        # I'm experimenting with the unittest.TestCase.assert* methods,
        # rather than using good ol' assert statements.
        self.assertTrue(self.hh.wants_to_handle(self.bogus_environ))

        self.assertFalse(
            self.hh.wants_to_handle({'PATH_INFO':'/helpme'}))

    def test_call(self):
        self.assertTrue(
            self.hh(self.bogus_environ, self.bogus_start_response))
