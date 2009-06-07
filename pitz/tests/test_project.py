# vim: set expandtab ts=4 sw=4 filetype=python:

import glob, os
from pitz.entity import Entity
from pitz.project import Project

from nose.tools import raises
from mock import Mock, patch

p = Project("Testing project")

tasks = [

    Entity(p, title='Clean cat box!', creator='person-matt',
        status='really important'),

    Entity(p, title='Shovel driveway', creator='person-matt',
        status='not very important'),
]

def teardown():
    for f in glob.glob('/tmp/*.yaml'):
        os.unlink(f)


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

@patch('__builtin__.open')
def test_to_yaml_file_1(o):
    
    p = Project("Bogus")
    p.to_yaml_file('bogus')


@patch('__builtin__.open')
@raises(ValueError)
def test_to_yaml_file_2(o):
    
    p = Project("Bogus")
    p.to_yaml_file()


@patch('__builtin__.open')
@patch('yaml.load')
@patch('__builtin__.globals')
def test_from_yaml_file_1(m1, m2, m3):

    # yaml.load(...) will return m2.
    m2.return_value = {
        'order_method_name':'bogus_method',
        'module':'pitz.project',
        'classname':'Project'}

    # globals() will return m3.
    m3.return_value = {'bogus_method': 99}

    p = Project("Bogus")
    b2 = p.from_yaml_file('aaa')
    assert b2.order_method == 99

def test_grep():

    p = Project("Bogus", pathname="/tmp") 
    e1 = Entity(title="bogus entity 1")
    e2 = Entity(title="bogus entity 2")
    p.append(e1)
    p.append(e2)
    p.save_entities_to_yaml_files()

    g1 = p.grep('bogus entity 1')
    assert e1 in g1
    assert e2 not in g1
    assert len(g1) == 1

    g2 = p.grep('BOGUS ENTITY 1')
    assert len(g2) == 0

    g3 = p.grep('BOGUS ENTITY 1', ignore_case=True)
    assert e1 in g3
    assert e2 not in g3
    assert len(g3) == 1
