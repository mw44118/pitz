# vim: set filetype=python :

import os
import pprint
import sys

from pitz.project import Project

from pitz import webapp
from pitz.webapp import handlers

pitzdir = '/home/matt/checkouts/pitz/pitzdir'

proj = Project.from_pitzdir(pitzdir)
proj.find_me()

app = webapp.SimpleWSGIApp(proj)

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

# This is what mod_wsgi looks for.
application = app

f = open('/tmp/pitz-app.log','w')
f.write(pprint.pformat(sys.path))
f.close()
