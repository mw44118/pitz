# vim: set expandtab ts=4 sw=4 filetype=python:

import unittest
import wsgiref.util

import mock

from pitz.project import Project
from pitz.entity import Entity
from pitz.webapp import handlers

class TestUpdate1(unittest.TestCase):

    def setUp(self):
        self.proj = Project()

        self.entity = Entity(
            self.proj,
            title='I am an entity!',
            flavor='chocolate')

        self.uh = handlers.Update(self.proj)
        self.bogus_environ = {}
        wsgiref.util.setup_testing_defaults(self.bogus_environ)
        self.bogus_environ['REQUEST_METHOD'] = 'POST'
        self.bogus_environ['PATH_INFO'] = '/by_frag/%(frag)s' % self.entity
        self.bogus_start_response = mock.Mock()

    def test_init(self):
        handlers.Update(self.proj)

    def test_wants_to_handle1(self):

        """
        Verify Update grabs POST requests with valid entity fragments.
        """

        print 'REQUEST_METHOD: %(REQUEST_METHOD)s' % self.bogus_environ
        print 'PATH_INFO: %(PATH_INFO)s' % self.bogus_environ

        frag = self.uh.extract_frag(self.bogus_environ['PATH_INFO'])
        print 'frag: %s' % frag
        print 'frag in self.proj: %s' % (frag in self.proj)

        self.assertEqual(
            self.uh,
            self.uh.wants_to_handle(self.bogus_environ))

    def test_wants_to_handle2(self):

        """
        Verify Update ignores POST requests with bogus entity fragments.
        """

        self.bogus_environ['PATH_INFO'] = '/by_frag/abc123'

        self.assertFalse(self.uh.wants_to_handle(self.bogus_environ))

    def test_wants_to_handle3(self):

        """
        Verify Update ignores GET requests, even if they have valid
        entity fragments.
        """

        self.bogus_environ['REQUEST_METHOD'] = 'GET'

        wants_to_handle = self.uh.wants_to_handle(self.bogus_environ)

        self.assertFalse(wants_to_handle)

    def test_call1(self):
        """
        Update the flavor from chocolate to vanilla.
        """

        # Put something in the wsgi input dictionary.
        something = 'flavor=vanilla'
        self.bogus_environ['wsgi.input'].write(something)
        self.bogus_environ['wsgi.input'].seek(0)
        self.bogus_environ['CONTENT_LENGTH'] = len(something)

        self.assertEqual(self.entity['flavor'], 'chocolate')
        self.uh(self.bogus_environ, self.bogus_start_response)
        self.assertEqual(self.entity['flavor'], 'vanilla')

    def test_call2(self):

        """
        Update the flavor from chocolate to ['chocolate', 'vanilla'].
        """

        # Put something in the wsgi input dictionary.
        something = 'flavor=chocolate&flavor=vanilla'

        self.bogus_environ['wsgi.input'].write(something)
        self.bogus_environ['wsgi.input'].seek(0)
        self.bogus_environ['CONTENT_LENGTH'] = len(something)

        self.assertEqual(self.entity['flavor'], 'chocolate')
        self.uh(self.bogus_environ, self.bogus_start_response)

        self.assertEqual(self.entity['flavor'],
            ['chocolate', 'vanilla'])
