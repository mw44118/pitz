# vim: set expandtab ts=4 sw=4 filetype=python:

import cgi
import mimetypes
import logging
import re
import urllib

from pitz import build_filter
from pitz.entity import Entity

log = logging.getLogger('pitz.webapp')

"""
/                                       p()
/?type=task                             p(type='task')
/?type=milestone&reached=0              p(type='milestone', reached=0)
/?owner=matt&owner=lindsey              p(owner=['matt', 'lindsey'])
/?type=activity                         p(type='activity')

/Person/by_title/matt/my_todo           Person.by_title('matt').my_todo
/Tag/all                                Tag.all()

/Task/all?status=unstarted              Tag.all().matches_dict(
                                            status=['unstarted'])

/Task/all/view/detailed?status=unstarted
    Task.all().matches_dict(
    status=['unstarted']).detailed_view

/Person/by_title/matt/my_todo
    Person.by_title('matt').my_todo

/Tag/all
    Tag.all()

/?owner=matt&owner=lindsey
    p(owner=['matt', 'lindsey'])

"""

class SimpleWSGIApp(object):

    def __init__(self, proj):
        self.proj = proj

    def __call__(self, environ, start_response):

        log.debug('PATH_INFO is %(PATH_INFO)s.' % environ)
        log.debug('QUERY_STRING is %(QUERY_STRING)s.' % environ)
        log.debug('HTTP_ACCEPT is %(HTTP_ACCEPT)s.' % environ)

        path_info = environ['PATH_INFO']
        qs = cgi.parse_qs(environ['QUERY_STRING'])
        http_accept = environ.get('HTTP_ACCEPT', '')

        all_classes = ('^/('
            + '|'.join([c.title() for c in self.proj.classes])
            + ')')

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

        # /Person/by_title/matt/my_todo
        # /Person/by_title/matt/my_todo/
        # /Person/by_title/matt/my_todo/detailed_view
        # /Person/by_title/matt/my_todo/detailed_view/
        # /Person/by_title/matt/my_todo/summarized_view
        # /Person/by_title/matt/my_todo/summarized_view/
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

        log.debug("404")

        status = '404 NOT FOUND'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)

        return ["Sorry, didn't match any patterns..."]

