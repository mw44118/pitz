# vim: set expandtab ts=4 sw=4 filetype=python:

class NoProject(Exception):
    """
    Indicates that this object can't do what you are asking it to do
    because it doesn't have a pitz.project.Project instance to work
    with.
    """

class ProjectYamlNotFound(Exception):
   """
    Indicates that the system couldn't find a project.yaml file when it
    tried to find one.
    """
