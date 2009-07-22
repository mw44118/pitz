# vim: set expandtab ts=4 sw=4 filetype=python:

import pickle, unittest, uuid

from pitz.entity import Entity, ImmutableEntity
from pitz.project import Project

from nose.tools import raises
from mock import Mock, patch

import yaml

e = None

def setup():
    global e
    e = Entity(title="bogus entity", a=1, b=2, c=3)

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

    m2.return_value = {'title':'bogus entity', 'a':1, 'b':2}

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
def test_to_html_file(o):
 
    global e
    e.to_html_file('bogus filepath')


def test_self_destruct():

    p = Project()
    p.pathname = '/tmp'
    e1 = Entity(p, title="e1", a=1, b=2)
    e1.to_yaml_file('/tmp')
    e1.self_destruct(p)


@raises(TypeError)
def test_allowed_types():

    Entity.allowed_types = {'frotz':Entity}
    e1 = Entity(title="e1", frotz='abc')


@raises(ValueError)
def test_allowed_values():

    Entity.allowed_values = {'frotz':[1,2]}
    e1 = Entity(title="e1", frotz='abc')


class TestImmutableEntity(object):

    def setUp(self):
        print("setting up")
        self.ie1 = ImmutableEntity(title="abc")

    def tearDown(self):
        print("tearing down")

    def test_from_yaml_file(self):

        p = Project()
        d = yaml.load(self.ie1.yaml)
        ImmutableEntity(p, **d)

    def test_already_instantiated(self):

        d = dict(title="abc")
        ie1 = ImmutableEntity(**d)

        frag1 = ie1.frag

        ie2 = ImmutableEntity(**d)

        assert id(ie1) == id(ie2)
        assert frag1 == ie2.frag, '%s != %s' % (frag1, ie2.frag)


class TestPicklingEntity(unittest.TestCase):
    """
    Pickle an entity that refers to other entities.
    """

    def setUp(self):

        self.p = Project()
        self.c = Entity(self.p, title="c")
        self.e = Entity(self.p, title="t", c=self.c)

    def tearDown(self):
        self.c.self_destruct(self.p)
        self.e.self_destruct(self.p)

    def test_pickle(self):

        s = pickle.dumps(self.e)
        assert self.e['c'] == self.c, self.e['c']
        assert isinstance(self.c, Entity)
        assert isinstance(self.e['c'], Entity)

    def test_unpickle(self):

        assert isinstance(self.e['c'], Entity) 
        assert self.e.project
        s = pickle.dumps(self.e)
        e = pickle.loads(s)
        assert id(e) != id(self.e)
        assert e.uuid == self.e.uuid
        assert isinstance(self.c, Entity)
        assert e['c'] == self.c, e['c']
        assert isinstance(self.e['c'], Entity) 
