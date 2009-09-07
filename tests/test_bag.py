# vim: set expandtab ts=4 sw=4 filetype=python:

import glob, os, unittest

import pitz
from pitz.entity import Entity
from pitz.bag import Bag
from pitz.project import Project

from nose.tools import raises
from nose import SkipTest

from mock import Mock, patch

b = Bag("Testing bag")

tasks = [

    Entity(b, title='Clean cat box!', creator='person-matt',
        status='really important'),

    Entity(b, title='Shovel driveway', creator='person-matt',
        status='not very important'),
]


def test_matches_dict_1():

    global b, tasks
    b.matches_dict(type='entity')


def test_new_bag():

    global tasks
    t1, t2 = tasks

    b2 = Bag(entities=tasks)

    assert t1 in b2
    assert t2 in b2

    b.order()
    

def test_append_1():

    b = Bag()
    b.append(pitz.entity.Entity(title='blah', status='irrelevant'))

    
def test_values():

    b = Bag()

    b.append(pitz.entity.Entity(title='blah', difficulty='easy',
        status='unstarted'))

    b.append(pitz.entity.Entity(title='blah', difficulty='hard',
        status='unstarted'))

    v = b.values('difficulty')
    assert len(v) == 2
    assert ('easy', 1) in v
    assert ('hard', 1) in v


@patch('__builtin__.open')
def test_to_csv(o):

    global b
    b.to_csv('bogus', 'title')
    

def test_order_1():

    global b
    b.order()


@raises(ValueError)
def test_order_2():

    b = Bag()
    b.append(pitz.entity.Entity(title='blah', difficulty='easy',
        status='unstarted'))

    b.append(pitz.entity.Entity(title='blah', difficulty='hard',
        status='unstarted'))
    
    b.order_method = None
    b.order()


def test_summarized_view():

    global b
    b.summarized_view


def test_detailed_view():

    global b
    b.detailed_view
    

def test_contents_1():

    b = Bag()
    b.append(Entity(title='A'))



def test_str():

    global b
    str(b)


def test_repr():

    global b
    repr(b)


def test_replace_objects_with_pointers():

    global b
    b.replace_objects_with_pointers()
    b.replace_pointers_with_objects()


def test_attributes():

    global b
    b.attributes


def test_values():

    global b
    a = b.attributes[0][0]
    b.values(a)


def test_getitem():

    global b
    e1 = b[0]

    assert b[0] == e1
    assert b[e1.uuid] == e1
    assert b[e1.uuid] == e1


@raises(ValueError)
def test_grep_1():

    """
    Verify we don't try to grep without a pathname.
    """

    global b
    b.grep('cat')


def test_html():

    global b
    b.html


@patch('__builtin__.open')
def test_to_html(o):
    
    global b
    b.to_html('bogus filepath')


def test_length():

    global b
    assert b.length == 2


class TestSorting1(unittest.TestCase):

    """
    Verify that we can sort on the pscore attribute.
    """


    def setUp(self):

        self.p = Project(title="test pscore")
        self.e1 = Entity(self.p, title="e1")
        self.e2 = Entity(self.p, title="e2")
        self.e3 = Entity(self.p, title="e3")
        self.e4 = Entity(self.p, title="e4")

        print("Original order of entities:")

        for e in self.p:
            print("%(title)s %(pscore)s" % e)


    def test_sort(self):

        assert self.p.length == 4

        assert self.p.order_method == pitz.by_pscore_and_milestone, \
        self.p.order_method

        for e in self.p:
            assert e['pscore'] == 0, e['pscore']

        assert list(self.p) == [self.e1, self.e2, self.e3, self.e4]

        self.e1['pscore'] = -10
        self.p.order()

        print("After first pscore change")
        for e in self.p:
            print("%(title)s %(pscore)s" % e)

        assert list(self.p) == [self.e2, self.e3, self.e4, self.e1]

        self.e3['pscore'] = 10
        self.p.order()
 
        print("After second pscore change")
        for e in self.p:
            print "%(title)s %(pscore)s" % e

        assert self.p == [self.e3, self.e2, self.e4, self.e1]


class TestSorting2(unittest.TestCase):

    """
    Sort entities based on their status attribute.
    """


    def setUp(self):

        self.p = Project(title="test simple score")

        class Status(Entity):
            pass

        self.finished = Status(self.p, title='finished', pscore=4)
        self.started = Status(self.p, title='started', pscore=3)
        self.unstarted = Status(self.p, title='unstarted', pscore=2)
        self.abandoned = Status(self.p, title='abandoned', pscore=1)

        self.e1 = Entity(self.p, title="e1", status=self.unstarted)
        self.e2 = Entity(self.p, title="e2", status=self.unstarted)
        self.e3 = Entity(self.p, title="e3", status=self.unstarted)
        self.e4 = Entity(self.p, title="e4", status=self.unstarted)


    def test_sort(self):

        entities = self.p(type='entity')

        self.e2['status'] = self.started
        self.e4['status'] = self.finished
        self.e3['pscore'] = self.e3['pscore'] + 1

        entities.order(pitz.by_milestone_status_pscore_created_time)

        assert entities.order_method \
        == pitz.by_milestone_status_pscore_created_time

        assert list(entities) == [self.e4, self.e2, self.e3, self.e1], \
        list(entities)


class TestBag(unittest.TestCase):


    def setUp(self):

        b = Bag('Everything', pathname='/tmp')

        e1 = Entity(title="example #1", creator="Matt",
            importance="Really important")

        e2 = Entity(title="example #2", creator="Matt",
            importance="not very")

        b.append(e1)
        b.append(e2)

        self.b = b


    def tearDown(self):

        if os.path.isfile('/tmp/project.pickle'):
            os.unlink('/tmp/project.pickle')

        for f in glob.glob('/tmp/*.yaml'):
            os.unlink(f)


    def test_matches_dict(self):

        e1, e2 = self.b
        assert e1.title == 'example #1', e1.title
        assert e2.title == 'example #2', e2.title

        unimportant_stuff = self.b.matches_dict(importance='not very')


    @patch('__builtin__.raw_input')
    def test_choose_value_1(self, m):

        """
        Pick the first option with choose_value.
        """

        e1, e2 = self.b
        assert e1.title == 'example #1', e1.title

        # When the test runs raw_input, it will automatically return 1.
        m.return_value = 1

        choice = self.b.choose_value('entity')
        assert choice == e1, choice


    @patch('__builtin__.raw_input')
    def test_choose_value_2(self, m):

        """
        Pick the default with choose_value.
        """

        e1, e2 = self.b
        assert e1.title == 'example #1', e1.title

        m.return_value = None 

        choice = self.b.choose_value('entity', 'DEFAULT')
        assert choice == 'DEFAULT', choice


    def test_by_frag(self):

        e1, e2 = self.b
        assert e1 == self.b.by_frag(e1.frag)


    def test_by_uuid_1(self):

        e1, e2 = self.b
        assert e1 == self.b.by_uuid(e1.uuid)


    def test_by_uuid_2(self):

        assert 'abc' == self.b.by_uuid('abc')


    def test_grep(self):

        for e in self.b:
            e.to_yaml_file('/tmp')

        assert self.b.grep('example').length == 2, \
        self.b.grep('example').length

        assert self.b.grep('EXAMPLE', ignore_case=True).length == 2
