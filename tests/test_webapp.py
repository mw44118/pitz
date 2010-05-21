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
        Entity(self.p, title="c")
        Entity(self.p, title="t")
        Person(self.p, title='matt')
        self.webapp = SimpleWSGIApp(self.p)

    def tearDown(self):

        for e in self.p:
            e.self_destruct(self.p)

        if os.path.exists('/tmp/project.pickle'):
            os.remove('/tmp/project.pickle')

    def mk_request(self, pi, qs, ha, expected_results):
        bogus_environ = dict(
            PATH_INFO=pi,
            QUERY_STRING=qs,
            HTTP_ACCEPT=ha)

        bogus_start_response = mock.Mock()
        results = self.webapp(bogus_environ, bogus_start_response)

        assert results == [expected_results], results

    def test_1(self):
        self.mk_request('/', '', 'text/plain', self.p.detailed_view)

    def test_2(self):
        self.mk_request('/', 'title=c', 'text/plain', 
            self.p.matches_dict(title='c').detailed_view)

    def test_3(self):
        self.mk_request('/', 'title=c&title=t', 'text/plain', 
            self.p.matches_dict(title=['c', 't']).detailed_view)

    def test_4(self):
        self.mk_request('/', 'title=c&title=t', 'application/x-pitz',
            self.p.matches_dict(title=['c', 't']).colorized_detailed_view)

    def test_5(self):
        self.mk_request('/Entity/by_title/c', '', 'text/plain',
            Entity.by_title('c').detailed_view)

    def test_6(self):
        self.mk_request('/Task/all/detailed_view', 'status=unstarted', 
            'text/plain', Task.all().matches_dict(
                status=['unstarted']).detailed_view)

    def test_7(self):
        self.mk_request('/Person/by_title/matt/my_todo', '', 
            'text/plain', Person.by_title('matt').my_todo.detailed_view)

    def test_8(self):
        self.mk_request('/Person/by_title/matt/my_todo/summarized_view', 
            '', 'text/plain', 
            Person.by_title('matt').my_todo.summarized_view)

    def test_9(self):
        self.mk_request('/',
            'owner=matt&owner=lindsey', 
            'text/plain', 
            self.p(owner=['matt', 'lindsey']))

    def test_10(self):

        for c, C in sorted(self.p.classes.items()):

            print("Working on %s..." % c)
            print("C is %s" % C)
            
            self.mk_request(
                '/%s/all' % c.title(), 
                '',
                'text/plain', str(C.all()))

            x = C(self.p, title='test_10')

            """
            self.mk_request(
                '/%s/by_title/test_10' % c.title(), 
                '',
                'text/plain', str(x))
            """
