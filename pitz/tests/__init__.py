# vim: set expandtab ts=4 sw=4 filetype=python:

from datetime import datetime
import pitz

tasks = [

    pitz.Task({'entity':'task-1', 'title':'Clean cat box!', 
        'type':'task'}),

    pitz.Task({'entity':'task-2', 'title':'Shovel driveway', 
        'type':'task'}),
]

people = [
    pitz.Entity({'entity':'person-matt', 'title':'Matthew Wilson',
        'type':'person'}),
    pitz.Entity({'entity':'person-lindsey', 'title':'Lindsey Wilson',
        'type':'person'}),
]

comments = [
    pitz.Entity({
        'entity':'comment-1',
        'title':'I hate cleaning the cat box!',
        'type':'comment',
        'commenter':'person-matt',
        'date':datetime.now(),
        'link':'task-1',
    }),

    pitz.Entity({
        'entity':'comment-2',
        'title':'But it needs to be done!',
        'type':'comment',
        'commenter':'person-lindsey',
        'date':datetime.now(),
        'link':'task-1',
    }),
]
