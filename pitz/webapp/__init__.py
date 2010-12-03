# vim: set expandtab ts=4 sw=4 filetype=python:

import cgi
import logging
import mimetypes
import os
import re
import urllib

import jinja2

from pitz import build_filter, PitzException
from pitz.entity import Entity
from pitz.webapp.handlers import DispatchingHandler

log = logging.getLogger('pitz.webapp')

class NoMatch(PitzException):
    """
    Indicates that we couldn't match this URL.
    """

class SimpleWSGIApp(DispatchingHandler):

    @classmethod
    def reply404(cls, start_response, msg=None):

        log.debug("404")

        start_response('404 NOT FOUND',
            [('content-type', 'text/plain')])

        if msg:
            return [msg]
        else:
            return ["Sorry, didn't match any patterns..."]

    def __call__(self, environ, start_response):

        log.debug('PATH_INFO is %(PATH_INFO)s.' % environ)
        log.debug('QUERY_STRING is %(QUERY_STRING)s.' % environ)
        log.debug('HTTP_ACCEPT is %(HTTP_ACCEPT)s.' % environ)

        h = self.dispatch(environ)

        if h:
            return h(environ, start_response)

        # Stuff below is the old junk that will one day be rewritten.

        path_info = environ['PATH_INFO']
        qs = cgi.parse_qs(environ['QUERY_STRING'])
        http_accept = environ.get('HTTP_ACCEPT', '')

        all_classes = ('^/('
            + '|'.join([c.title() for c in self.proj.classes])
            + ')')

        try:

            if re.search('^/$', path_info):

                log.debug("matched the slash...")

                if qs:
                    results = self.proj(**qs)
                else:
                    results = self.proj

                status = '200 OK'

                if 'application/x-pitz' in http_accept \
                and 'detailed_view' in path_info:

                    log.debug('a')

                    headers = [('Content-type', 'application/x-pitz')]
                    start_response(status, headers)
                    return [str(results.colorized_detailed_view)]

                if 'application/x-pitz' in http_accept:
                    log.debug('e')
                    headers = [('Content-type', 'application/x-pitz')]
                    start_response(status, headers)
                    return [str(results.colorized_detailed_view)]

                if 'detailed_view' in path_info:

                    log.debug('b')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results.detailed_view)]

                if 'summarized_view' in path_info:

                    log.debug('c')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results.colorized_detailed_view)]

                else:

                    log.debug('d')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results)]

            pattern = (all_classes +
                r'/all/?(detailed_view|summarized_view)?/?$')

            m2 = re.search(pattern, path_info)

            if m2:

                log.debug('Matched m2...')

                classname, view_type = m2.groups()
                cls = self.proj.classes[classname.lower()]
                results = cls.all()

                if qs:
                    results = results.matches_dict(**qs)

                status = '200 OK'

                if 'application/x-pitz' in http_accept \
                and 'detailed_view' in path_info:

                    log.debug('a')

                    headers = [('Content-type', 'application/x-pitz')]
                    start_response(status, headers)
                    return [str(results.colorized_detailed_view)]

                if 'detailed_view' in path_info:

                    log.debug('b')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results.detailed_view)]

                if 'summarized_view' in path_info:

                    log.debug('c')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results.colorized_detailed_view)]

                else:

                    log.debug('d')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results)]

            m3 = re.search(all_classes +
                r'/by_title/([^/]+)/?'
                '(detailed_view|summarized_view)?/?$', path_info)

            if m3:

                log.debug('matched m3. groups: %s' % list(m3.groups()))

                classname, title, view_type = m3.groups()

                cls = self.proj.classes[classname.lower()]
                results = cls.by_title(urllib.unquote(title))

                if qs:
                    results = results.matches_dict(**qs)

                status = '200 OK'

                if 'application/x-pitz' in http_accept \
                and 'detailed_view' in path_info:

                    log.debug('a')

                    headers = [('Content-type', 'application/x-pitz')]
                    start_response(status, headers)
                    return [str(results.colorized_detailed_view)]

                if 'detailed_view' in path_info:

                    log.debug('b')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results.detailed_view)]

                if 'summarized_view' in path_info:

                    log.debug('c')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results.summarized_view)]

                else:

                    log.debug('d')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results)]

            m4 = re.search(r'^/Person/by_title/([^/]+)/my_todo/?'
                '(detailed_view|summarized_view)?/?$', path_info)

            if m4:

                log.debug('matched m4. groups: %s' % list(m4.groups()))
                title, view_type = m4.groups()
                Person = self.proj.classes['person']
                results = Person.by_title(urllib.unquote(title)).my_todo

                if qs:
                    results = results.matches_dict(**qs)

                status = '200 OK'

                if 'application/x-pitz' in http_accept \
                and 'detailed_view' in path_info:

                    log.debug('a')

                    headers = [('Content-type', 'application/x-pitz')]
                    start_response(status, headers)
                    return [str(results.colorized_detailed_view)]

                if 'detailed_view' in path_info:

                    log.debug('b')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results.detailed_view)]

                if 'summarized_view' in path_info:

                    log.debug('c')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results.summarized_view)]

                else:

                    log.debug('d')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results)]

            m5 = re.search('/by_frag/([^/]+)/?'
                '(detailed_view|summarized_view|rst_detailed_view|rst_summarized_view|one_line_view)?/?$', path_info)

            if m5:

                log.debug('matched m5. groups: %s' % list(m5.groups()))

                frag, view_type = m5.groups()

                results = self.proj.by_frag(frag)

                status = '200 OK'

                if 'application/x-pitz' in http_accept \
                and 'detailed_view' in path_info:

                    log.debug('a')

                    headers = [('Content-type', 'application/x-pitz')]
                    start_response(status, headers)
                    return [str(results.colorized_detailed_view)]

                if 'detailed_view' in path_info:

                    log.debug('b')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results.detailed_view)]

                if 'summarized_view' in path_info:

                    log.debug('c')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results.summarized_view)]

                else:

                    log.debug('d')

                    headers = [('Content-type', 'text/html')]
                    start_response(status, headers)
                    return [str(
                        getattr(results, view_type) if view_type
                        else results.html)]

            m6 = re.search('/by_frag/([^/]+)/my_todo/?'
                '(detailed_view|summarized_view)?/?$', path_info)

            if m6:

                log.debug('matched m6. groups: %s' % list(m6.groups()))

                frag, view_type = m6.groups()

                results = self.proj.by_frag(frag)
                Person = self.proj.classes['person']

                if not isinstance(results, Person):
                    return self.reply404(start_response)

                results = results.my_todo

                if qs:
                    results = results.matches_dict(**qs)

                status = '200 OK'

                if 'application/x-pitz' in http_accept \
                and 'detailed_view' in path_info:

                    log.debug('a')

                    headers = [('Content-type', 'application/x-pitz')]
                    start_response(status, headers)
                    return [str(results.colorized_detailed_view)]

                if 'detailed_view' in path_info:

                    log.debug('b')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results.detailed_view)]

                if 'summarized_view' in path_info:

                    log.debug('c')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(results.summarized_view)]

                else:

                    log.debug('d')

                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [str(
                        getattr(results, view_type) if view_type
                        else results)]

            raise NoMatch(path_info)

        except NoMatch, ex:

            return self.reply404(start_response)
