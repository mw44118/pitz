# vim: set expandtab ts=4 sw=4 filetype=python:

import glob, os, random, time, unittest
from pitz.entity import Entity
from pitz.project import Project
import pitz

from nose import SkipTest
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

    for f in glob.glob('/tmp/*.yaml') + [
        '/tmp/project.pickle',
        '/tmp/index.html']:

        if os.path.exists(f):
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
@patch('pickle.dump')
def test_to_yaml_file_1(m1, m2):

    p = Project("Bogus")
    p.to_yaml_file('bogus-pathname')


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
    m3.return_value = {'bogus_method': lambda e1, e2: 1}

    p = Project("Bogus")
    b2 = p.from_yaml_file('xyz')
    assert b2.order_method == m3.return_value['bogus_method']


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

class TestPicklingProject(unittest.TestCase):

    def setUp(self):

        self.p = Project()
        self.c = Entity(self.p, title="c")
        self.e = Entity(self.p, title="t", c=self.c)


    def tearDown(self):
        self.c.self_destruct(self.p)
        self.e.self_destruct(self.p)

        if os.path.exists('/tmp/project.pickle'):
            os.remove('/tmp/project.pickle')


    def test_to_pickle1(self):

        self.assertRaises(
            ValueError,
            self.p.to_pickle)


    def test_to_pickle2(self):

        self.p.to_pickle('/tmp')
        assert os.path.exists('/tmp/project.pickle')


    def test_unpickle(self):

        assert not os.path.exists('/tmp/project.pickle')
        self.p.to_pickle('/tmp')
        assert os.path.exists('/tmp/project.pickle')
        new_p = Project.from_pickle('/tmp/project.pickle')
        assert self.p.length == new_p.length
        assert new_p.length
        for e in new_p:
            assert e.project


class TestFindPitzdir(unittest.TestCase):

    def setUp(self):
        os.mkdir('/tmp/walkup')
        os.mkdir('/tmp/walkup/pitzdir')
        os.mkdir('/tmp/walkup/pitzdir/foo')
        os.mkdir('/tmp/walkdown')
        os.mkdir('/tmp/walkdown/foo')
        os.mkdir('/tmp/walkdown/foo/bar')
        os.mkdir('/tmp/walkdown/foo/bar/baz')
        os.mkdir('/tmp/walkdown/foo/bar/baz/pitzdir')

        os.mkdir('/tmp/deadend')
        os.mkdir('/tmp/deadend/foo')
        os.mkdir('/tmp/deadend/foo/bar')
        os.mkdir('/tmp/deadend/foo/bar/baz')

        os.environ['PITZDIR'] = 'xxx'

    def tearDown(self):

        os.chdir(os.environ['HOME'])
        os.rmdir('/tmp/walkdown/foo/bar/baz/pitzdir')
        os.rmdir('/tmp/walkdown/foo/bar/baz')
        os.rmdir('/tmp/walkdown/foo/bar')
        os.rmdir('/tmp/walkdown/foo')
        os.rmdir('/tmp/walkdown')
        os.rmdir('/tmp/walkup/pitzdir/foo')
        os.rmdir('/tmp/walkup/pitzdir')
        os.rmdir('/tmp/walkup')

        os.rmdir('/tmp/deadend/foo/bar/baz')
        os.rmdir('/tmp/deadend/foo/bar')
        os.rmdir('/tmp/deadend/foo')
        os.rmdir('/tmp/deadend')


    def test_1(self):
        """
        Verify we can use the parameter
        """

        assert Project.find_pitzdir('/tmp/walkup/pitzdir') \
        == '/tmp/walkup/pitzdir'

    def test_2(self):
        """
        Verify we check os.environ.
        """

        os.environ['PITZDIR'] = '/tmp/walkup/pitzdir'

        assert Project.find_pitzdir() == '/tmp/walkup/pitzdir'

    @raises(IOError)
    def test_3(self):
        """
        Verify we catch invalid values.
        """

        Project.find_pitzdir('/tmp/boguspitzdir')


    def test_4(self):
        """
        Verify we can walk up and find pitzdir.
        """

        os.chdir('/tmp/walkup/pitzdir/foo')
        assert Project.find_pitzdir() == '/tmp/walkup/pitzdir'


    def test_5(self):
        """
        Verify we can walk down and find the pitzdir.
        """

        os.chdir('/tmp/walkdown')

        pitzdir_location = Project.find_pitzdir(walkdown=True)

        assert pitzdir_location == '/tmp/walkdown/foo/bar/baz/pitzdir', \
        pitzdir_location


    def test_6(self):

        os.chdir('/tmp/deadend')
        self.assertRaises(pitz.ProjectNotFound, Project.find_pitzdir)


class TestFromPitzdir(unittest.TestCase):

    def setUp(self):

        self.p = Project(pathname='/tmp')
        self.p.to_yaml_file()
        self.p.to_pickle()

    def tearDown(self):

        for f in glob.glob('/tmp/*.yaml'):
            os.unlink(f)

        if os.path.isfile('/tmp/project.pickle'):
            os.unlink('/tmp/project.pickle')


    def test_fresh_pickle(self):
        """
        Verify we use the pickle when we can.
        """

        p = Project.from_pitzdir('/tmp')
        assert p.loaded_from == 'pickle', p.loaded_from


    def test_stale_pickle(self):
        """
        Verify we use the yaml files when the pickle is too old.
        """

        stat = os.stat('/tmp/project.pickle')

        os.utime('/tmp/project.pickle',
            (stat.st_atime-1, stat.st_mtime-1))

        print("pickle file: %s"
            % os.stat('/tmp/project.pickle').st_mtime)

        print("newest yaml file: %s"
            % max([os.stat(f).st_mtime for f in glob.glob('/tmp/*.yaml')]))

        p = Project.from_pitzdir('/tmp')
        assert p.loaded_from == 'yaml', p.loaded_from


    def test_from_yaml_files(self):
        """
        Verify we can use the yaml files when no pickle exists.
        """

        os.unlink('/tmp/project.pickle')

        p = Project.from_pitzdir('/tmp')
        assert p.loaded_from == 'yaml', p.loaded_from


class TestProject(unittest.TestCase):

    def test_html_then_pickle(self):

        p = Project(pathname='/tmp')
        p.to_html('/tmp')
        p.save_entities_to_yaml_files()


class TestSaveToYaml(unittest.TestCase):

    def test_missing_pathname(self):

        p = Project(
            entities=[
                Entity(title='abc'),
                Entity(title='def'),
                Entity(title='ghi')])

        self.assertRaises(
            ValueError,
            p.save_entities_to_yaml_files)


class TestSetupDefaults(unittest.TestCase):

    def test_setup_defaults(self):

        """
        Verify the project calls setup_defaults.
        """

        p = Project(
            entities=[
                Entity(title='abc'),
                Entity(title='def'),
                Entity(title='ghi')])

        m = Mock()

        p.classes = dict(bogus_entity=m)

        p.setup_defaults()

        assert ('setup_defaults', (p, ), {}) in m.method_calls, \
        m.method_calls


class TestProperties(unittest.TestCase):

    def setUp(self):

        self.p = Project(
            entities=[
                Entity(title='abc'),
                Entity(title='def'),
                Entity(title='ghi')])


    def test_recent_activity(self):

        assert self.p.recent_activity.order_method \
        == pitz.by_descending_created_time


    def test_activities(self):

        assert self.p.activities.order_method \
        == pitz.by_descending_created_time


    def test_milestones(self):
        assert not self.p.milestones

    def test_components(self):
        assert not self.p.components

    def test_tasks(self):
        assert not self.p.tasks

    def test_people(self):
        assert not self.p.people

    def test_comments(self):
        assert not self.p.comments

    def test_estimates(self):
        assert not self.p.estimates

    def test_statuses(self):
        assert not self.p.statuses

    def test_unscheduled(self):
        assert not self.p.unscheduled

    def test_started(self):
        assert not self.p.started

    def test_me(self):
        assert self.p.me is None
