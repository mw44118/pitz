# vim: set expandtab ts=4 sw=4 filetype=python:

from pitz.entity import Entity
from pitz.project import Project

from nose.tools import raises
from mock import Mock, patch

e = Entity(a=1, b=2, c=3)

def test_summarized_view():
    global e
    e.summarized_view

def test_replace_objects_with_pointers():

    e1 = Entity(title="e1", a=1, b=2)
    e2 = Entity(title="e2", a=2, b=3)

    e1['friend'] = e2

    e1.replace_objects_with_pointers()
    assert e1['friend'] == e2.uuid, e1['friend']


def test_replace_pointers_with_objects():

    p = Project()
    e1 = Entity(p, title="e1", a=1, b=2)
    e2 = Entity(p, title="e2", a=2, b=3)

    e1['friend'] = e2.uuid

    e1.replace_pointers_with_objects()
    assert e1['friend'] == e2, e1['friend']


@patch('__builtin__.open')
@patch('yaml.load')
def test_from_yaml_file_1(m1, m2):

    m2.return_value = {'a':1, 'b':2}

    global e

    e2 = e.from_yaml_file('bogus')
    assert e2['a'] == 1
    assert e2['b'] == 2

@patch('__builtin__.open')
@patch('yaml.load')
def test_from_yaml_file_2(m1, m2):

    m2.return_value = {}

    global e

    assert e.from_yaml_file('bogus') == None


def test_html():
    global e
    e.html


@patch('__builtin__.open')
def test_to_html(o):
 
    global e
    e.to_html('bogus filepath')


def test_self_destruct():

    p = Project()
    p.pathname = '/tmp'
    e1 = Entity(p, title="e1", a=1, b=2)
    e1.to_yaml_file('/tmp')
    e1.self_destruct(p)

    
