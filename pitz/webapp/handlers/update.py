# vim: set expandtab ts=4 sw=4 filetype=python:

import logging
import re
import urlparse

from pitz.webapp.handlers import Handler
from pitz.entity.task import Task

log = logging.getLogger('pitz.webapp.handlers.update')

class Update(Handler):

    """
    Accepts POST requests to update an attribute on an entity.

    A post like this::

        POST /by_frag/abc123

        title=your+mom+is+so+fat&attributes=title

    Is vaguely similar to::

        e = proj['abc123']
        e['title'] = 'your mom is so fat'

    """

    def wants_to_handle(self, environ):

        # Gauntlet pattern... Look for lots of different reasons to
        # return False (or None, here), and after all those, return True
        # (or self, in this case).
        if environ['REQUEST_METHOD'] != 'POST':
            return

        frag = self.extract_frag(environ['PATH_INFO'])

        if frag not in self.proj.entities_by_frag:
            return

        # End of the gauntlet.
        return self

    def __call__(self, environ, start_response):

        log.debug('Inside the top of __call__...')

        frag = self.extract_frag(environ['PATH_INFO'])
        e = self.proj.by_frag(frag)

        log.debug('Found entity %(frag)s' % e)

        raw_post_data = environ['wsgi.input'].read(
            int(environ['CONTENT_LENGTH']))

        log.debug('raw_post_data is %s' % raw_post_data)

        post_data = urlparse.parse_qs(raw_post_data)

        log.debug('parsed post_data is %s' % post_data)

        status = '302 FOUND'
        headers = [('Location', 'http://google.com')]
        start_response(status, headers)

        log.debug('About to return an empty list...')

        return []



class UpdateTask(Handler):

    def wants_to_handle(self, environ):

        if environ['REQUEST_METHOD'] != 'POST':
            return

        frag = self.extract_frag(environ['PATH_INFO'])

        if frag not in self.proj.entities_by_frag:
            return

        ent = self.proj.entities_by_frag[frag]

        if not isinstance(ent, Task):
            return

        return self

