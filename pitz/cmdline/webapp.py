# vim: set expandtab ts=4 sw=4 filetype=python:

import logging
import os
from wsgiref.simple_server import make_server

import pitz
from pitz.cmdline import setup_options
from pitz.project import Project

from pitz import webapp
from pitz.webapp import handlers

def pitz_webapp():

    """
    This function gets run by the command-line script pitz-webapp.
    """

    p = setup_options()

    p.add_option('-p', '--port', help='HTTP port (default is 9876)',
       type='int', action='store', default=9876)

    options, args = p.parse_args()
    pitz.setup_logging(getattr(logging, options.log_level))

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    app = webapp.SimpleWSGIApp(proj)

    # Remember that the order that you add handlers matters.  When a
    # request arrives, the app starts with the first handler added and
    # asks it if wants to handle that request.  So, the default handler
    # (if you make one) belongs at the end.

    # Consider this section below the same as the urls.py file in
    # django.

    static_files = os.path.join(os.path.split(
        os.path.dirname(__file__))[0], 'static')

    app.handlers.append(handlers.FaviconHandler(static_files))
    app.handlers.append(handlers.StaticHandler(static_files))
    app.handlers.append(handlers.HelpHandler(proj))
    app.handlers.append(handlers.Update(proj))
    app.handlers.append(handlers.ByFragHandler(proj))
    app.handlers.append(handlers.EditAttributes(proj))
    app.handlers.append(handlers.Project(proj))
    app.handlers.append(handlers.Team(proj))

    httpd = make_server('', options.port, app)
    print "Serving on port %d..." % options.port
    httpd.serve_forever()
