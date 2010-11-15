# vim: set expandtab ts=4 sw=4 filetype=python:

import logging
import os
import re

import jinja2

log = logging.getLogger('pitz.webapp.handlers')

class HelpHandler(object):

    """
    Handles the GET /help request.
    """

    def wants_to_handle(self, environ):

        if environ['PATH_INFO'] == '/help':
            return self

    def __call__(self, environ, start_response):

        """
        Return a screen of help about the web app.
        """

        # Figure out the path to the jinja2templates.
        jinja2dir = os.path.join(
            os.path.split(os.path.dirname(__file__))[0],
            'jinja2templates')

        # Set up a template loader.
        self.e = jinja2.Environment(
            extensions=['jinja2.ext.loopcontrols'],
            loader=jinja2.FileSystemLoader(jinja2dir))

        t = self.e.get_template('help.html')

        status = '200 OK'
        headers = [('Content-type', 'text/html')]

        start_response(status, headers)
        return [str(t.render(title='Pitz Webapp Help'))]


class FaviconHandler(object):

    def __init__(self):

        self.favicon_guts = open(
            os.path.join(os.path.split(os.path.dirname(__file__))[0],
            'static', 'favicon.ico')).read()

    def wants_to_handle(self, environ):

        if environ['PATH_INFO'] == '/favicon.ico':
            return self

    def __call__(self, environ, start_response):
        status = '200 OK'
        headers = [('Content-type', 'image/x-icon')]
        start_response(status, headers)

        return [self.favicon_guts]


class StaticHandler(object):

    def wants_to_handle(self, environ):

        if environ['PATH_INFO'].startswith('/static'):
            return self

    def __call__(self, environ, start_response):

        status = '200 OK'

        filename = self.extract_filename(environ['PATH_INFO'])
        f = self.find_file(filename)

        if filename.endswith('.js'):
            content_type = 'application/x-javascript'

        elif filename.endswith('.css'):
            content_type = 'text/css'

        else:
            content_type = 'text/plain'

        headers = [('Content-type', content_type)]
        start_response(status, headers)

        return [f.read()]

    @staticmethod
    def find_file(filename):
        """
        Return an open file for filename.
        """

        return open(os.path.join(
            os.path.split(os.path.dirname(__file__))[0],
            'static', filename))

    @staticmethod
    def extract_filename(path_info):

        """
        >>> StaticHandler.extract_filename('/static/pitz.css')
        'pitz.css'
        """

        return re.match(
            r'^/static/(?P<filename>.+)$',
            path_info).groupdict()['filename']

class ByFragHandler(object):

    def __init__(self, proj):
        self.proj = proj

    def wants_to_handle(self, environ):
        if environ['PATH_INFO'].startswith('/by_frag'):
            return self

    def __call__(self, environ, start_response):

        results = self.proj.by_frag(
            self.extract_frag(environ['PATH_INFO']))

        status = '200 OK'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)

        return [str(results.html)]

    @staticmethod
    def extract_frag(path_info):

        """
        >>> ByFragHandler.extract_frag('/by_frag/9f1c76')
        '9f1c76'
        """

        return re.match(
            r'^/by_frag/(?P<frag>.+)$',
            path_info).groupdict()['frag']


class Project(object):

    def __init__(self, proj):
        self.proj = proj

    def wants_to_handle(self, environ):

        if environ['PATH_INFO'] in ('/', '/Project'):
            return self

    def __call__(self, environ, start_response):

        status = '200 OK'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)

        return [str(self.proj.html)]

class Handler(object):

    def __init__(self, proj):
        self.proj = proj

        jinja2dir = os.path.join(
            os.path.split(os.path.dirname(__file__))[0],
            'jinja2templates')

        # Set up a template loader.
        self.e = jinja2.Environment(
            extensions=['jinja2.ext.loopcontrols'],
            loader=jinja2.FileSystemLoader(jinja2dir))

class Greedy(Handler):

    def wants_to_handle(self, environ):
        return True

    def __call__(self, environ, start_response):

        """
        Look for a template named the same as PATH_INFO or return a 404.
        """

        status = '200 OK'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)

        return [str(self.proj.html)]
