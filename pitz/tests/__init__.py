# vim: set expandtab ts=4 sw=4 filetype=python:

from datetime import datetime
import pitz

b = pitz.Bag()

tasks = [

    pitz.Task(b, {'title':'Clean cat box!', 
        'type':'task', 'creator':'person-matt'}),

    pitz.Task(b, {'title':'Shovel driveway', 
        'type':'task', 'creator':'person-matt'}),
]

