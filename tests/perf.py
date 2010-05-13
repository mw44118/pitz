# vim: set expandtab ts=4 sw=4 filetype=python:

"""
Stuff in here is for profiling and timing.
"""

import cProfile
import timeit

commands = {

    'my_todo': """p.me.my_todo.detailed_view""",
    'me': """p.me""",
    'todo': """p.todo.detailed_view""",
}

setup = """
from pitz.project import Project
p = Project.from_pitzdir(Project.find_pitzdir())
"""

def prof_this(k):

    return cProfile.runctx(commands[k], globals(), locals(),
        filename='%s.profile')

def time_this(k, number=100):
    return min(timeit.Timer(commands[k], setup).repeat(3, number))
