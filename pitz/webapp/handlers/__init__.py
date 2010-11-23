# vim: set expandtab ts=4 sw=4 filetype=python:

import datetime
import logging
import os
import re
import time

import jinja2

import pitz.jinja2templates

log = logging.getLogger('pitz.webapp.handlers')

class Handler(object):

    def __init__(self, proj):
        self.proj = proj

        jinja2dir = os.path.dirname(pitz.jinja2templates.__file__)

        # Set up a template loader.
        self.e = jinja2.Environment(
            extensions=['jinja2.ext.loopcontrols'],
            loader=jinja2.FileSystemLoader(jinja2dir))

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
            os.path.split(
                os.path.split(os.path.dirname(__file__))[0])[0],
            'jinja2templates')

        # Set up a template loader.
        self.e = jinja2.Environment(
            extensions=['jinja2.ext.loopcontrols'],
            loader=jinja2.FileSystemLoader(jinja2dir))

        t = self.e.get_template('help.html')

        status = '200 OK'
        headers = [('Content-Type', 'text/html')]

        start_response(status, headers)
        return [str(t.render(title='Pitz Webapp Help'))]

class StaticHandler(object):

    timefmt = '%a, %d %b %Y %H:%M:%S GMT'

    def __init__(self, static_files):
        self.static_files = static_files

    def wants_to_handle(self, environ):

        if environ['PATH_INFO'].startswith('/static'):
            return self

    def __call__(self, environ, start_response):

        log.debug(environ)

        filename = self.extract_filename(environ['PATH_INFO'])

        f = self.find_file(filename)

        modified_time = self.figure_out_modified_time(
            os.path.join(self.static_files, filename))

        modified_time_header = modified_time.strftime(self.timefmt)

        if 'HTTP_IF_MODIFIED_SINCE' in environ:

            if_modified_since = datetime.datetime.strptime(
                environ['HTTP_IF_MODIFIED_SINCE'],
                self.timefmt)

        if 'HTTP_IF_MODIFIED_SINCE' in environ \
        and if_modified_since >= modified_time:

            headers = [
                ('Content-Type', self.figure_out_content_type(filename)),
                ('Last-Modified', modified_time_header),
            ]

            start_response('304 Not Modified', headers)

            return []

        else:

            headers = [
                ('Content-Type', self.figure_out_content_type(filename)),
                ('Last-Modified', modified_time_header),
            ]

            start_response('200 OK', headers)

            return [f.read()]

    def find_file(self, filename):
        """
        Return an open file for filename.
        """

        return open(os.path.join(
            self.static_files,
            filename))

    @staticmethod
    def extract_filename(path_info):

        """
        >>> StaticHandler.extract_filename('/static/pitz.css')
        'pitz.css'
        """

        return re.match(
            r'^/static/(?P<filename>.+)$',
            path_info).groupdict()['filename']

    @staticmethod
    def figure_out_modified_time(favicon_path):

        tt = time.gmtime(os.stat(favicon_path).st_mtime)
        return datetime.datetime(*tt[:6])


    @staticmethod
    def figure_out_content_type(filename):

        """
        >>> StaticHandler.figure_out_content_type('abc.js')
        'application/x-javascript'
        >>> StaticHandler.figure_out_content_type('abc.css')
        'text/css'
        >>> StaticHandler.figure_out_content_type('x.pdf')
        'text/plain'
        """

        if filename.endswith('.js'):
            content_type = 'application/x-javascript'

        elif filename.endswith('.css'):
            content_type = 'text/css'

        else:
            content_type = 'text/plain'

        return content_type


class FaviconHandler(StaticHandler):

    def __init__(self, static_dir):

        super(FaviconHandler, self).__init__(static_dir)

        self.favicon_path = os.path.join(
            self.static_files, 'favicon.ico')

        self.favicon_guts = open(self.favicon_path).read()

        self.last_modified = self.figure_out_modified_time(
            self.favicon_path).strftime(self.timefmt)

    def wants_to_handle(self, environ):

        if environ['PATH_INFO'] == '/favicon.ico':
            return self

    def __call__(self, environ, start_response):
        status = '200 OK'

        headers = [
            ('Content-Type', 'image/x-icon'),
            ('Last-Modified', self.last_modified),
        ]

        start_response(status, headers)

        return [self.favicon_guts]


class ByFragHandler(object):

    def __init__(self, proj):
        self.proj = proj
        self.pattern = re.compile(r'^/by_frag/......$')

    def wants_to_handle(self, environ):

        log.info('self.__class__.__name__ is %s'
            % self.__class__.__name__)

        log.info("PATH_INFO is %(PATH_INFO)s" % environ)

        if self.pattern.match(environ['PATH_INFO']):
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

        >>> ByFragHandler.extract_frag(
        ...     '/by_frag/9f1c76/edit-attributes')
        '9f1c76'
        """

        return re.match(
            r'^/by_frag/(?P<frag>.{6}).*$',
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

class EditAttributes(ByFragHandler):

    def __init__(self, proj):
        self.proj = proj
        self.pattern = re.compile(r'^/by_frag/....../edit-attributes$')

    def __call__(self, environ, start_response):

        task = self.proj.by_frag(
            self.extract_frag(environ['PATH_INFO']))

        tmpl = task.e.get_template('task-edit-attributes.html')

        status = '200 OK'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)

        return [str(tmpl.render(task=task))]

from pitz.webapp.handlers.team import Team
