# vim: set expandtab ts=4 sw=4 filetype=python:

import pickle, unittest, uuid

from pitz.entity import Entity
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

    def test_from_yaml_file(self):

        p = Project()
        d = yaml.load(self.ie1.yaml)
        Entity(p, **d)

    def test_already_instantiated(self):

        d = dict(title="abc")
        ie1 = Entity(**d)

        frag1 = ie1.frag

        ie2 = Entity(**d)

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

        e.summarized_view
        e.detailed_view

class TestMatchesDict1(unittest.TestCase):


    def setUp(self):

        self.p = Project(title="TestMatchesDict")

        self.important = Entity(self.p, title='Important!!!')

        Entity.allowed_types['priority'] = Entity

        self.e = Entity(self.p, title='Clean cat box', creator='Matt',
            tags=['boring', 'chore'], priority=self.important)


    def test_matches_dict_1(self):

        """
        Verify matches_dict handles scalars and list comparisons.
        """

        assert self.e.matches_dict(creator='Matt') == self.e
        assert self.e.matches_dict(creator='Nobody') == None
        assert self.e.matches_dict(tags=['boring', 'chore']) == self.e
        assert self.e.matches_dict(tags='boring') == self.e
        assert self.e.matches_dict(tags='chore') == self.e
        assert self.e.matches_dict(creator=['Matt']) == self.e
        assert self.e.matches_dict(creator=['Matt', 'Nobody']) == self.e

        assert self.e.matches_dict(
            creator=['Matt', 'Nobody'],
            tags=['fun']) == None

        assert self.e.matches_dict(
            creator=['Matt', 'Nobody'],
            tags=['fun', 'boring']) == self.e


    def test_matches_dict_2(self):

        """
        Verify we can match entities by using their UUID
        """

        assert self.e.matches_dict(priority=self.important) == self.e

        assert self.e.matches_dict(
            priority=self.important.uuid) == self.e

        assert self.e.matches_dict(
            priority=self.important.frag) == self.e


    def test_matches_dict_3(self):
        """
        Verify we can match entities by using their title.
        """

        assert 'priority' in self.e.allowed_types

        assert self.e.matches_dict(
            priority=self.important.title) == self.e, \
        "Lookup using title failed"


class TestEntityComparisons(unittest.TestCase):

    def setUp(self):

        self.p = Project(title="TestEntityComparisons")
        self.e1 = Entity(self.p, title="e1", pscore=1)
        self.e2 = Entity(self.p, title="e2", pscore=2)
        self.e3 = Entity(self.p, title="e3", pscore=3)

    def test_comparision(self):
        print("e1 pscore is %(pscore)s" % self.e1)
        print("e2 pscore is %(pscore)s" % self.e2)
        assert self.e1 < self.e2, cmp(self.e1, self.e2)

class TestAppending(unittest.TestCase):

    def setUp(self):

        self.p = Project(title="TestAppending")
        self.e1 = Entity(title="e1")


    def test_append(self):
        """
        Verify the _set_project property does an append.
        """

        assert self.e1 not in self.p

        self.e1.project = self.p

        assert self.e1 in self.p


