# vim: set expandtab ts=4 sw=4 filetype=python:

"""
Stuff in here is for profiling and timing.
"""

import cProfile
import pstats
import timeit

commands = {

    'my_todo': """p.me.my_todo.detailed_view""",
    'me': """p.me""",
    'todo': """p.todo.detailed_view""",
}

def prof(command, outfilename):
    cProfile.runctx(command, globals(), locals(), filename=outfilename)


