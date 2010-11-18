# vim: set expandtab ts=4 sw=4 filetype=python:

from pitz.webapp.handlers import Handler

class Team(Handler):

    def wants_to_handle(self, environ):

        if environ['PATH_INFO'] == '/team':
            return self

    def __call__(self, environ, start_response):

        t = self.e.get_template('team.html')

        status = '200 OK'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)

        return [str(t.render(proj=self.proj))]
