# vim: set expandtab ts=4 sw=4 filetype=python:

import os
import unittest

import mock

from pitz.project import Project
from pitz.entity import Entity, Person, Task
from pitz.webapp import SimpleWSGIApp

class TestWebApp(unittest.TestCase):

    def setUp(self):

        self.p = Project(title='Bogus project for testing webapp')
        self.c = Entity(self.p, title="c")
        self.e = Entity(self.p, title="t", c=self.c)
        self.webapp = SimpleWSGIApp(self.p)

    def tearDown(self):
        self.c.self_destruct(self.p)
        self.e.self_destruct(self.p)

        if os.path.exists('/tmp/project.pickle'):
            os.remove('/tmp/project.pickle')

    def test_1(self):

        bogus_environ = dict(
            PATH_INFO='/',
            QUERY_STRING='',
            HTTP_ACCEPT='text/plain')

        bogus_start_response = mock.Mock()
        results = self.webapp(bogus_environ, bogus_start_response)

        assert results == [self.p.detailed_view]


    def test_2(self):

        bogus_environ = dict(
            PATH_INFO='/',
            QUERY_STRING='title=c',
            HTTP_ACCEPT='text/plain')

        bogus_start_response = mock.Mock()
        results = self.webapp(bogus_environ, bogus_start_response)

        assert results == [
            self.p.matches_dict(
                title='c').detailed_view], results


    def test_3(self):

        bogus_environ = dict(
            PATH_INFO='/',
            QUERY_STRING='title=c&title=t',
            HTTP_ACCEPT='text/plain')

        bogus_start_response = mock.Mock()
        results = self.webapp(bogus_environ, bogus_start_response)

        assert results == [
            self.p.matches_dict(
                title=['c', 't']).detailed_view], results


    def test_4(self):

        bogus_environ = dict(
            PATH_INFO='/',
            QUERY_STRING='title=c&title=t',
            HTTP_ACCEPT='application/x-pitz')

        bogus_start_response = mock.Mock()
        results = self.webapp(bogus_environ, bogus_start_response)

        assert results == [
            self.p.matches_dict(
                title=['c', 't']).colorized_detailed_view], results


    def test_5(self):

        bogus_environ = dict(
            PATH_INFO='/Entity/by_title/c',
            QUERY_STRING='',
            HTTP_ACCEPT='text/plain')

        bogus_start_response = mock.Mock()
        results = self.webapp(bogus_environ, bogus_start_response)

        expected_results = Entity.by_title('c').detailed_view

        print(expected_results)

        assert results == [expected_results], results


    def test_6(self):

        bogus_environ = dict(
            PATH_INFO='/Task/all/detailed_view?status=unstarted',
            QUERY_STRING='',
            HTTP_ACCEPT='text/plain')

        bogus_start_response = mock.Mock()
        results = self.webapp(bogus_environ, bogus_start_response)

        expected_results = Task.all().matches_dict(
            status=['unstarted']).detailed_view

        print(expected_results)
        assert results == [expected_results], results


    def test_7(self):

        bogus_environ = dict(
            PATH_INFO='/Person/by_title/matt/my_todo',
            QUERY_STRING='',
            HTTP_ACCEPT='text/plain')

        bogus_start_response = mock.Mock()
        results = self.webapp(bogus_environ, bogus_start_response)

        expected_results = Person.by_title('matt').my_todo

        assert results == [expected_results], results


    def test_8(self):

        bogus_environ = dict(

            PATH_INFO='/Person/by_title/matt/my_todo/summarized_view',
            QUERY_STRING='status=unstarted',
            HTTP_ACCEPT='text/plain')

        bogus_start_response = mock.Mock()
        results = self.webapp(bogus_environ, bogus_start_response)

        expected_results = Person.by_title('matt')\
        .my_todo.matches_dict(status=['unstarted']).summarized_view

        assert results == [expected_results], results


    def test_9(self):

        bogus_environ = dict(

            PATH_INFO='/',
            QUERY_STRING='owner=matt&owner=lindsey',
            HTTP_ACCEPT='text/plain')

        bogus_start_response = mock.Mock()
        results = self.webapp(bogus_environ, bogus_start_response)

        expected_results = self.p(owner=['matt', 'lindsey'])

        assert results == [str(expected_results)], results
