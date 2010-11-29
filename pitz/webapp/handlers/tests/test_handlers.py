# vim: set expandtab ts=4 sw=4 filetype=python:

import datetime
import os
import rfc822
import time
import unittest
import urllib

import mock

from pitz.project import Project

from pitz.entity import Entity, Person, Task, Status, Milestone, \
Activity, Estimate, Tag, Comment, Component

import pitz.static

from pitz import webapp
from pitz.webapp import handlers

class TestStaticHandler1(unittest.TestCase):

    def test_1(self):

        """
        Verify I can make an instance of a StaticHandler.
        """

        sh = handlers.StaticHandler(os.path.join(os.path.split(
                os.path.dirname(__file__))[0],
            'pitz', 'static'))

class TestStaticHandler2(unittest.TestCase):

    def setUp(self):

        pitz_static_files = os.path.dirname(pitz.static.__file__)

        self.sh = handlers.StaticHandler(pitz_static_files)

        seconds = os.stat(os.path.join(
            pitz_static_files, 'pitz.css')).st_mtime

        time_tuple = time.gmtime(seconds)

        self.modified_time = datetime.datetime(*time_tuple[:6])


    def test_1(self):
        """
        Verify the handler reples with an accurate Last-Modified header.
        """

        bogus_start_response = mock.Mock()

        # Send a request to the handler.
        self.sh({'PATH_INFO': '/static/pitz.css'}, bogus_start_response)

        assert bogus_start_response.called

        assert bogus_start_response.call_args[0][0] == '200 OK', \
        bogus_start_response.call_args[0][0]

        headers = bogus_start_response.call_args[0][1]

        # Make sure that there's a Last-Modified header.
        values = [v for (k, v) in headers if k == 'Last-Modified']
        assert len(values) == 1, headers

        last_modified_header = values[0]

        assert self.modified_time == datetime.datetime(
            *(rfc822.parsedate( last_modified_header))[:6])


    def test_2(self):

        """
        Verify handler sends 304 for cached content.

        When the request includes an If-Modified-Since header, and the
        content hasn't been updated since that date, verify the handler
        replies with a 304.
        """

        bogus_start_response = mock.Mock()

        if_modified_since = self.modified_time.strftime(
            handlers.StaticHandler.timefmt)

        # Send a request to the handler.
        self.sh(
            {
                'PATH_INFO': '/static/pitz.css',
                'HTTP_IF_MODIFIED_SINCE': if_modified_since
            },
            bogus_start_response)

        assert bogus_start_response.called

        assert bogus_start_response.call_args[0][0] \
        == '304 Not Modified', \
        bogus_start_response.call_args[0][0]

        headers = bogus_start_response.call_args[0][1]

        # Make sure that there's a Last-Modified header.
        values = [v for (k, v) in headers if k == 'Last-Modified']
        assert len(values) == 1, headers

        last_modified_header = values[0]

        assert self.modified_time == datetime.datetime(
            *(rfc822.parsedate( last_modified_header))[:6])

    def test_3(self):
        """
        When the request includes an If-Modified-Since header, and the
        content WAS updated since that date, verify the handler replies
        with a 200.
        """

class TestFaviconHandler1(unittest.TestCase):

    def test_instantiate(self):
        handlers.FaviconHandler(os.path.dirname(pitz.static.__file__))

class TestFaviconHandler2(unittest.TestCase):

    def setUp(self):

        self.fh = handlers.FaviconHandler(os.path.dirname(
            pitz.static.__file__))

    def test_wants_to_handle(self):

        assert self.fh.wants_to_handle({'PATH_INFO':'/favicon.ico'})

    def test_call(self):

        assert self.fh({}, mock.Mock())
