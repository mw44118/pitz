# vim: set expandtab ts=4 sw=4 filetype=python:

import re

from pitz.webapp.handlers import ByFragHandler

class EditAttributes(ByFragHandler):

    """
    Draws a form to allow editing attributes on a task.
    """

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
