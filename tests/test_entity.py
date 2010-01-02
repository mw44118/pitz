# vim: set expandtab ts=4 sw=4 filetype=python:

import glob, os, pickle, unittest, uuid

from pitz.entity import *
from pitz.bag import Bag, Project
from pitz import NoProject

from nose.tools import raises
from mock import Mock, patch

import yaml

e = None

@raises(NoProject)
def test_no_project():

    e = Entity(title="blah123")
    print(e.project)
    e.replace_pointers_with_objects()


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

        assert e.update_modified_time == True


class TestMatchesDict(unittest.TestCase):


    def setUp(self):

        self.p = Project(title="TestMatchesDict")

        self.important = Entity(self.p, title='Important!!!')

        Entity.allowed_types['priority'] = Entity

        Entity.allowed_types['components'] = [Entity]

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


    def test_order_independence_of_query(self):

        """
        Test two attributes with lists as values.
        """

        assert not self.e.matches_dict(creator=['Matt'],
            title=['DO NOT MATCH'])

        assert not self.e.matches_dict(creator=['DO NOT MATCH'],
            title=['Clean cat box'])


    def test_order_independence_of_subquery(self):

        """
        Test two attributes with lists, and one of the lists has a title
        as an element.
        """

        assert not self.e.matches_dict(
            priority=[self.important.title], # this one matches
            tags=['DOES NOT MATCH']          # but not this one.
        )


    def test_matches_dict_2(self):

        """
        Verify we can match entities by using their UUID
        """

        assert self.e.matches_dict(priority=self.important) == self.e

        assert self.e.matches_dict(priority=self.important.uuid) == self.e

        frag = self.important.frag

        assert self.e.matches_dict(priority=frag) == self.e


    def test_matches_dict_3(self):
        """
        Verify we can match entities by using their title.
        """

        assert 'priority' in self.e.allowed_types

        print("self.e['priority'] is %(priority)s" % self.e)

        assert self.e.matches_dict(
            priority=self.important.title) == self.e, \
        "Lookup using title failed"


    def test_matches_dict_4(self):
        """
        Verify we can match with lists of titles.
        """

        print("self.e['priority'] is %(priority)s" % self.e)

        assert self.e.matches_dict(
            priority=[self.important.title]) == self.e, \
        "Lookup using list of titles failed"


    def test_matches_dict_5(self):
        """
        Verify we can match with lists of titles.
        """

        assert self.e.matches_dict(priority=["bogus"]) is None, \
        "Matching too much!"


    def test_matches_dict_6(self):
        """
        Verify we can match with lists of frags.
        """

        print("self.e['priority'] is %(priority)s" % self.e)

        assert self.e.matches_dict(
            priority=[self.important.frag]) == self.e, \
        "Lookup using list of frags failed"


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


class TestHilariousBug(unittest.TestCase):

    """
    This bug is hilarious because it took me about 14 hours to
    figure it out.

    When an entity changes its UUID, some entities have pointers to the
    old UUID and others will have pointers to the new UUID.

    The bug was that the entity's new UUID wasn't added to the
    project.entities_by_uuid dictionary, so, some entities couldn't
    replace pointers with objects.

    Entity.__new__ checks if an entity already exists with the same type
    and title.  If it does, __new__ returns a reference to that one.

    Meanwhile, Entity.__init__ uses a uuid parameter or generates a
    random one.

    So, the bug happens like this:

    1.  Somehow an Entity gets generated with a random UUID.

    2.  Later an Entity with the same type and title gets made, but it
        passes in its own UUID.  So the __new__ method returns a
        reference to the original Entity and then blows away the uuid
        attribute from before with the new one.

    As long as other entities had references to the object and not to
    the UUID, nothing goes wrong.

    But when entities only store references to UUIDs, there's a chance
    that somebody might not be able to replace the pointer (the UUID)
    with the object (the entity).
    """

    def tearDown(self):

        for f in glob.glob('/tmp/*.yaml'):
            os.unlink(f)


    def test_1(self):
        """
        Simple case of hilarious bug.
        """

        p = Project()
        est1 = Entity(p, title="blah")
        est1_uuid = est1.uuid
        assert est1_uuid in p.entities_by_uuid

        est2 = Entity(p, title=est1.title, uuid=uuid.uuid4())
        est2_uuid = est2.uuid

        assert est2 is est1
        assert est1_uuid != est2_uuid
        assert est1_uuid in p.entities_by_uuid
        assert p.entities_by_uuid[est1_uuid] is est2
        assert est2.uuid in p.entities_by_uuid
        assert p.entities_by_uuid[est2_uuid] is est2


    def test_2(self):

        p = Project()
        est1 = Entity(p, title='4 days')
        est1_uuid = est1.uuid

        e1 = Entity(p, title='some task', estimate=est1)
        e1.replace_objects_with_pointers()

        est2 = Entity(p, title=est1.title, uuid=uuid.uuid4())
        assert est2 is est1
        assert est1_uuid != est2.uuid

        e2 = Entity(p, title='another task', estimate=est2)
        e2.replace_objects_with_pointers()

        assert e1['estimate'] != e2['estimate'], est2['estimate']

        e1.replace_pointers_with_objects()
        e2.replace_pointers_with_objects()

        assert e1['estimate'] == e2['estimate'], est2['estimate']


class TestNewMethod(unittest.TestCase):


    def test1(self):

        a = Entity(title="a")

        print("id(Entity.already_instantiated): %s"
            % id(Entity.already_instantiated))

        print("Entity.already_instantiated has %d entities cached"
            % len(Entity.already_instantiated))

        b = Entity(title="a")

        print("Entity.already_instantiated has %d entities cached"
            % len(Entity.already_instantiated))

        assert a.uuid == b.uuid


    def test2(self):

        p = Project()

        a = Entity(p, title="a")
        a2 = Entity(title="a")

        assert a is a2
        assert a2.project

class TestEntity(unittest.TestCase):


    def test_detailed_view(self):

        f = Entity(title='foo', description='fibityfoo')

        assert isinstance(f.detailed_view, basestring), \
        type(f.detailed_view)

        assert f['title'] in f.detailed_view


    def test_summarized_view(self):

        f = Entity(title='foo', description='fibityfoo')
        assert isinstance(f.summarized_view, str)
        assert f['title'] in f.summarized_view


    def test_required_fields_1(self):

        """
        When loading from yaml, verify we don't overwrite required fields.
        """

        f = Entity(title='foo', description='fibityfoo')

        f2 = Entity.from_yaml_file(f.to_yaml_file('/tmp'))

        assert f2['description'] == 'fibityfoo', f2['description']


    def test_required_fields_2(self):

        """
        Verify entities retrieved from already_instantiated don't
        overwrite required fields.
        """

        f = Entity(title='foo', description='fibityfoo')
        f2 = Entity(title='foo')
        assert f2['description'] == 'fibityfoo', f2['description']


    def test_already_instantiated_1(self):

        """
        Verify parameters passed in init apply even when entity has
        already been instantiated once.
        """

        f1 = Entity(title='foo', description='fibityfoo')
        f2 = Entity(title='foo', description='yoink')
        assert f2['description'] == 'yoink', f2['description']

        f3 = Entity(title='foo')
        assert f3['description'] == 'yoink', f3['description']

        assert f1 is f2 is f3


    def test_created_by_1(self):

        """
        Verify nothing breaks when no current user is set.
        """

        p = Project()
        e = Entity(p, title="entity")
        assert 'created_by' not in e


    def test_created_by_2(self):

        p = Project()
        p.current_user = Person(p, title='matt')
        e = Entity(p, title="entity")
        assert e['created_by'] == p.current_user


    def test_new_task(self):
        """
        Verify we can make a new task.
        """

        p = Project()

        t = Task(p, title='Clean cat box please!',
            status=Status(title='unstarted'),
            creator='Matt',
            description='It is gross!')

        assert t.uuid == t['uuid']


    def test_missing_attributes_replaced_with_defaults(self):
        """
        Verify we fill in missing attributes with defaults.
        """

        t = Task(title="bogus")
        assert t['status'] == Status(title='unstarted')


    def test_update_task_status(self):

        t1 = Task(title='t1')

        t1['status'] = Status(title='unstarted')
        t1['status'] = Status(title='finished')


    def test_comment_on_task(self):

        p = Project()
        t1 = Task(title='t1')

        c = Comment(p, who_said_it="matt",
            entity=t1,
            title="blah blah")

        comments_on_t1 = p(type='comment', entity=t1)
        assert len(comments_on_t1) == 1
        assert comments_on_t1[0]['title'] == 'blah blah'


    def test_convert_to_allowed_types(self):
        """
        Verify we coerce to an allowed type.
        """

        e = Entity(title='blah', pscore='99')
        assert e['pscore'] == 99, 'pscore is %(pscore)s' % e




class TestMisc(unittest.TestCase):


    def setUp(self):

        self.p = Project()
        p = self.p
        p.append(Task(title='Draw new accounting report', priority=2))
        p.append(Task(title='Improve speed of search page', priority=0))

        p.append(Task(title='Add animation to site logo',
            estimate=Estimate(title="straightforward", points=2)))

        p.append(Task(title='Write "forgot password?" feature',
            priority=1, estimate=Estimate(title="straightforward", points=2)))

        p.append(Task(title='Allow customer to change contact information',
            priority=2, estimate=Estimate(title="straightforward", points=2)))

        p.append(Task(title='Allow customer to change display name',
            priority=2, estimate=Estimate(title="easy", points=1)))

        p.append(Milestone(title="1.0"))
        p.append(Milestone(title="2.0"))

    @raises(NoProject)
    def test_noproject(self):
        m = Milestone(title="Bogus milestone")
        m.tasks

    def test_show_milestones(self):
        """
        List every milestone.
        """

        p = self.p

        for m in p.milestones:
            m.todo

    def test_milestone_todo(self):

        p = self.p

        for m in p.milestones:
            m.todo

    def test_milestone_summarized_view(self):

        p = self.p

        for m in p.milestones:
            m.summarized_view


    def test_comments(self):

        p = self.p
        t = Task(p, title="wash dishes")
        z = Comment(p, entity=t, title="I don't want to", who_said_it="Matt")
        c = t.comments[0]
        c.summarized_view
        c.detailed_view

    def test_project_todo(self):

        p = self.p
        p.todo


    def test_project_tasks(self):

        p = self.p
        p.tasks

    def test_project_people(self):

        p = self.p
        p.people

    def test_project_comments(self):

        p = self.p
        p.comments

    def test_unscheduled(self):

        p = self.p
        p.unscheduled


    def test_abandon_task(self):

        p = self.p
        t = Task(p, title="wash dishes")
        t.abandon()

    @raises(NoProject)
    def test_component(self):

        c1 = Component(title="Component A")
        c1.tasks

    def test_components_property(self):

        p = self.p
        c1 = Component(p, title="Component A")
        assert p.components.length == 1, p.components
        assert c1 in p.components

    def test_started_property(self):

        p = self.p
        started_tasks = p(type='task', status='started')
        assert p.started.length == started_tasks.length


    def test_from_uid(self):
        """
        Use the os.getuid() to look up a person.
        """

        matt = Person(
            title='W. Matthew Wilson')


    def test_repr_after_replace_objects_with_pointers(self):


        p = Project(
            entities=[
                Task(title="wash dishes",
                    status=Status(title="unstarted"))])

        t = Task(title="wash dishes")
        assert t in p

        assert isinstance(t['status'], Entity)
        t.replace_objects_with_pointers()
        assert isinstance(t['status'], uuid.UUID)

        t.summarized_view


    @patch('__builtin__.raw_input')
    def test_choose_many(self, m):

        a = Entity(title="aaa")
        b = Entity(title="bbb")
        c = Entity(title="ccc")

        m.return_value = "1  3"

        results = Entity.choose_many_from_already_instantiated()
        assert len(results) == 2


class TestAllowedTypes(unittest.TestCase):

    def setUp(self):

        class E(Entity):

            allowed_types = dict(
                owner=Entity,
                related_entities=[Entity],
                pscore=int,
                junk=list)

        self.E = E


    def test_setitem(self):

        """
        Test allowed_types dictionary.
        """

        e1 = self.E(title='e1')
        e2 = self.E(title='e2')

        e1.__setitem__('related_entities', [e2])
        e1.__setitem__('related_entities', Bag(entities=[e2]))

        self.assertRaises(
            TypeError,
            e1.__setitem__,
            'related_entities',
            [1,2,3])

        self.assertRaises(
            TypeError,
            e1.__setitem__,
            'related_entities',
            e2)

        e1.__setitem__('owner', Entity(title="matt"))
        e1.__setitem__('junk', [1,2,3])
        e1.__setitem__('pscore', '99')


    @patch('pitz.entity.Entity.choose_many_from_already_instantiated')
    def test_edit(self, m):
        """
        Verify we ask for many instances of an attribute when
        appropriate.
        """

        e1 = self.E(title='e1')
        e2 = self.E(title='e2')
        e3 = self.E(title='e3')

        m.return_value = [e2, e3]

        e1.edit('related_entities')
        assert m.called

