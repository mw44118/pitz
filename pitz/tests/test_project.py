# vim: set expandtab ts=4 sw=4 filetype=python:

from pitz.entity import Entity
from pitz.project import Project

from nose.tools import raises

p = Project("Testing project")

tasks = [

    Entity(p, title='Clean cat box!', creator='person-matt',
        status='really important'),

    Entity(p, title='Shovel driveway', creator='person-matt',
        status='not very important'),
]


def test_to_and_from_yaml_files_1():

    global p
    p.save_entities_to_yaml_files('/tmp')

    Project().load_entities_from_yaml_files('/tmp')

@raises(ValueError)
def test_load_entities_1():

    p = Project("Bogus")
    p.load_entities_from_yaml_files()


@raises(ValueError)
def test_load_entities_2():

    p = Project("Bogus")
    p.load_entities_from_yaml_files('nonexistent directory')


@raises(ValueError)
def test_save_entities_1():

    p = Project("Bogus")
    p.save_entities_to_yaml_files()

@raises(ValueError)
def test_save_entities_1():

    p = Project("Bogus")
    p.save_entities_to_yaml_files('nonexistent directory')
