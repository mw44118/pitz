# vim: set expandtab ts=4 sw=4 filetype=python:

import unittest
import wsgiref.util

import mock

from pitz.webapp import handlers

class TestEditAttributes1(unittest.TestCase):

    def setUp(self):
        self.bogus_project = mock.Mock()
        self.ea = handlers.EditAttributes(self.bogus_project)

    def test_init(self):
        ea = handlers.EditAttributes(self.bogus_project)

        self.assertTrue(ea.pattern)

        self.assertTrue(
            ea.pattern.match('/by_frag/abc123/edit-attributes'))

    def test_wants_to_handle(self):

        bogus_environ = {'PATH_INFO': '/by_frag/abc123/edit-attributes'}
        wsgiref.util.setup_testing_defaults(bogus_environ)

        self.assertEqual(
            self.ea,
            self.ea.wants_to_handle(bogus_environ))
