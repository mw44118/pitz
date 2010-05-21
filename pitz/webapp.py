# vim: set expandtab ts=4 sw=4 filetype=python:

import cgi
import mimetypes
import logging
import re
import uuid

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

        self.matcher = re.compile(
            r'/(Entity|Task|Milestone|Person|Tag|Estimate)'
            '/by_title/(\w+)')

    def __call__(self, environ, start_response):

        log.debug('PATH_INFO is %(PATH_INFO)s.' % environ)
        log.debug('QUERY_STRING is %(QUERY_STRING)s.' % environ)
        log.debug('HTTP_ACCEPT is %(HTTP_ACCEPT)s.' % environ)

        path_info = environ['PATH_INFO']
        qs = cgi.parse_qs(environ['QUERY_STRING'])
        http_accept = environ.get('HTTP_ACCEPT', '')

        m = re.search(r'^/Entity/by_title/(\w+)/?$', path_info)

        if m:
            Entity = self.proj.classes['entity']
            results = Entity.by_title(*m.groups())

            status = '200 OK'

            if 'application/x-pitz' in http_accept \
            and 'detailed_view' in path_info:
                headers = [('Content-type', 'application/x-pitz')]
                start_response(status, headers)
                return [str(results.colorized_detailed_view)]

            if 'detailed_view' in path_info:
                headers = [('Content-type', 'text/plain')]
                start_response(status, headers)
                return [str(results.detailed_view)]

            if 'summarized_view' in path_info:
                headers = [('Content-type', 'text/plain')]
                start_response(status, headers)
                return [str(results.colorized_detailed_view)]

            else:
                headers = [('Content-type', 'text/plain')]
                start_response(status, headers)
                return [str(results.detailed_view)]

        m2 = re.search(
            r'^/(Status|Estimate|Milestone|Entity|Person|Tag|Task)'
            r'/all/?(detailed_view|summarized_view)?/?$', path_info)

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

        m3 = re.search(
            r'^/Person/by_title/(\w+)/my_todo/?'
            '(detailed_view|summarized_view)?/?', path_info)

        if m3:
            title, view = m3.groups()
            Person = self.proj.classes['person']
            results = Person.by_title(title).my_todo

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
                return [str(results.detailed_view)]

        if qs:
            filtered = self.proj(**qs)

        else:
            filtered = self.proj

        if 'application/x-pitz' in environ.get('HTTP_ACCEPT', ''):
            status = '200 OK'
            headers = [('Content-type', 'text/plain')]
            start_response(status, headers)
            return [str(filtered.colorized_detailed_view)]

        else:
            status = '200 OK'
            headers = [('Content-type', 'text/plain')]
            start_response(status, headers)
            return [str(filtered.detailed_view)]

