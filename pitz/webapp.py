# vim: set expandtab ts=4 sw=4 filetype=python:

import mimetypes, logging, uuid

from pitz import build_filter

log = logging.getLogger('pitz.cmdline')

class SimpleWSGIApp(object):

    def __init__(self, proj):
        self.proj = proj

    def __call__(self, environ, start_response):

        """
        Shows a single entity in detail:
        /entity/d734c3c0-0d25-4d3d-9d25-6ab32d13d65a

        Return the file /tmp/a.txt:
        /attached_files/tmp/a.txt   

        Views of lots of stuff:

        /project                            Lists everything.
        /project?type=task                  Lists all tasks
        /project?type=task&status=def456    Tasks with status def456
        /?type=task&status=started          Started tasks

        """

        log.debug('PATH_INFO is %(PATH_INFO)s' % environ)
        log.debug('QUERY_STRING is %(QUERY_STRING)s' % environ)

        path_info = environ['PATH_INFO']

        if path_info.startswith('/entity'):

            junk, entity_label, uuidstr = path_info.split('/')
            u = uuid.UUID(uuidstr)
            entity = self.proj[u]

            status = '200 OK'
            headers = [('Content-type', 'text/html')]
            start_response(status, headers)

            return [str(entity.html)]


        elif path_info.startswith('/static'):

            filename = path_info[7:]

            file_type, encoding = mimetypes.guess_type(filename)

            if type:
                headers = [('Content-type', file_type)]
            else:
                headers = [('Content-type', 'application/octet-stream')]

            status = '200 OK'
            start_response(status, headers)

            return [str(open(filename).read())]


        elif path_info.startswith('/todo'):

            status = '200 OK'
            headers = [('Content-type', 'text/html')]
            start_response(status, headers)

            b = self.proj.todo

            if environ['QUERY_STRING']:

                b = b.matches_dict(**build_filter(
                    environ['QUERY_STRING'].split('&')))

            return [str(b.html)]

        # Just return the project page as the fallback.
        else:

            status = '200 OK'
            headers = [('Content-type', 'text/html')]
            start_response(status, headers)

            b = self.proj

            if environ['QUERY_STRING']:

                b = b.matches_dict(**build_filter(
                    environ['QUERY_STRING'].split('&')))

            return [str(b.html)]
