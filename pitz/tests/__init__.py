# vim: set expandtab ts=4 sw=4 filetype=python:

from datetime import datetime
import pitz

tasks = [

    pitz.Task({'name':'task-1', 'title':'Clean cat box!', 
        'type':'task', 'creator':'person-matt'}),

    pitz.Task({'name':'task-2', 'title':'Shovel driveway', 
        'type':'task', 'creator':'person-matt'}),
]

