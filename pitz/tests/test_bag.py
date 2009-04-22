# vim: set expandtab ts=4 sw=4 filetype=python:

import pitz
from pitz.entity import Entity
from pitz.bag import Bag

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


def test_matches_dict():

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
def test_to_yaml_file_1(o):
    
    global b
    b.to_yaml_file('bogus')


@patch('__builtin__.open')
@raises(ValueError)
def test_to_yaml_file_2(o):
    
    global b
    b.to_yaml_file()


@patch('__builtin__.open')
@patch('yaml.load')
@patch('__builtin__.globals')
def test_from_yaml_file_1(m1, m2, m3):

    m2.return_value = {'order_method_name':'bogus_method'}
    m3.return_value = {'bogus_method': 99}

    global b
    b2 = b.from_yaml_file('aaa')
    assert b2.order_method == 99


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

    Bag().contents

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

