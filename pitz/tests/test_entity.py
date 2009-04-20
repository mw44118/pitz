# vim: set expandtab ts=4 sw=4 filetype=python:

from pitz.entity import Entity

from mock import Mock, patch

e = Entity(a=1, b=2, c=3)

def test_summarized_view():
    global e
    e.summarized_view

def test_replace_objects_with_pointers():

    global e
    f = Entity(a=2, e=e)

    f.pointers = ['e']
    f.replace_objects_with_pointers()


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
