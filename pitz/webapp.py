# vim: set expandtab ts=4 sw=4 filetype=python:

import cgi
import mimetypes
import logging
import re
import uuid

from pitz import build_filter

log = logging.getLogger('pitz.webapp')

class SimpleWSGIApp(object):

    def __init__(self, proj):
        self.proj = proj

        self.matcher = re.compile(
            r'/(Entity|Task|Milestone|Person|Tag|Estimate)'
            '/by_title/(\w+)')

    def __call__(self, environ, start_response):

        log.debug('PATH_INFO is %(PATH_INFO)s.' % environ)
        log.debug('QUERY_STRING is %(QUERY_STRING)s.' % environ)
        log.debug('HTTP_ACCEPT is %(HTTP_ACCEPT)s.' % environ)

        path_info = environ['PATH_INFO']
        qs = environ['QUERY_STRING']
        http_accept = environ.get('HTTP_ACCEPT', '')

        parts = path_info.split('/')

        log.debug('split PATH_INFO %s into %s'
            % (path_info, parts))

        m = self.matcher.search(path_info)

        if m:

            log.debug("Got a match...")

            Entity = self.proj.classes['entity']
            results = Entity.by_title(parts[3])

            status = '200 OK'
            headers = [('Content-type', 'text/plain')]
            start_response(status, headers)

            if 'application/x-pitz' in http_accept \
            and 'detailed_view' in path_info:
                return [str(results.colorized_detailed_view)]

            if 'detailed_view' in path_info:
                return [str(results.detailed_view)]

            if 'summarized_view' in path_info:
                return [str(results.colorized_detailed_view)]

            else:
                return [str(results.detailed_view)]

        if qs:
            filtered = self.proj(**cgi.parse_qs(qs))

        else:
            filtered = self.proj


        if 'application/x-pitz' in environ.get('HTTP_ACCEPT', ''):
            return [str(filtered.colorized_detailed_view)]

        else:
            return [str(filtered.detailed_view)]

