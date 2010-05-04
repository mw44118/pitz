# vim: set expandtab ts=4 sw=4 filetype=python:

import cgi
import mimetypes
import logging
import uuid

from pitz import build_filter

log = logging.getLogger('pitz.webapp')

class SimpleWSGIApp(object):

    def __init__(self, proj):
        self.proj = proj

    def __call__(self, environ, start_response):

        log.debug('PATH_INFO is %(PATH_INFO)s' % environ)
        log.debug('QUERY_STRING is %(QUERY_STRING)s' % environ)
        log.debug('HTTP_ACCEPT is %(HTTP_ACCEPT)s' % environ)

        path_info = environ['PATH_INFO']
        qs = environ['QUERY_STRING']

        # Filter the project.
        filtered = self.proj(**cgi.parse_qs(environ['QUERY_STRING']))

        # Figure out what format to return.

        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)

        if 'application/x-pitz' in environ.get('HTTP_ACCEPT'):
            return [str(filtered.colorized_detailed_view)]

        else:
            return [str(filtered.detailed_view)]
