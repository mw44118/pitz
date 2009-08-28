# vim: set expandtab ts=4 sw=4 filetype=python:

import glob, os, unittest
from datetime import datetime
import yaml

import pitz
from pitz.bag import Bag
from pitz.projecttypes.simplepitz import *

from nose.tools import raises
from nose import SkipTest


class TestSimpleTask(unittest.TestCase):

    def setUp(self):

        self.b = Bag()

        self.tasks = [

            Task(self.b, title='Clean the cat box!', creator='Matt',
                status=Status(self.b, title='unstarted')),

            Task(self.b, title='Shovel driveway', creator='Matt',
                status=Status(self.b, title='unstarted')),
        ]

        self.t1, self.t2 = self.tasks


    def tearDown(self):

        """
        Delete any files we created.
        """
        for f in glob.glob('/tmp/task-*.yaml'):
            os.unlink(f)


    def test_new_bag(self):

        b = Bag(entities=self.tasks)

        assert self.t1 in b
        assert self.t2 in b


    def test_show_task(self):
        """
        Verify that we show related information.
        """

        t1, t2 = self.tasks

        print
        print(t1.detailed_view)


    def test_new_task(self):
        """
        Verify we can make a new task.
        """

        b = Bag()

        t = Task(b, title='Clean cat box please!', 
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


    def test_summarized_view(self):

        t1, t2 = self.tasks
        assert isinstance(t1.summarized_view, str)
        assert t1['title'] in t1.summarized_view


    def test_update_task_status(self):

        t1, t2 = self.tasks

        t1['status'] = Status(title='unstarted')
        t1['status'] = Status(title='finished')


    def test_comment_on_task(self):

        t1, t2 = self.tasks
        b = self.b

        c = Comment(b, who_said_it="matt",
            entity=t1,
            title="blah blah")

        comments_on_t1 = b(type='comment', entity=t1)
        assert len(comments_on_t1) == 1
        assert comments_on_t1[0]['title'] == 'blah blah'


    def test_view_tasks_for_matt(self):

        p = Project("Matt's stuff")
        matt = Person(p, title='Matt')

        t = Task(p, title='Clean cat box now', owner=matt,
            status=Status(p, title='unstarted'))

        tasks_for_matt = p(type='task', owner=matt)
        assert t in tasks_for_matt

        
    def test_view_tasks_for_matt_and_in_next_milestone(self):

        p = Project("Matt's stuff")
        matt = Person(p, title='Matt')
        m = Milestone(p, title='Next Milestone')

        t = Task(p, title='Clean cat box again', owner=matt, milestone=m,
            status=Status(title='unstarted'))

        tasks_for_matt_in_next_milestone = p(type='task', owner=matt, 
            milestone=m)

        assert t in tasks_for_matt_in_next_milestone


    def test_yaml(self):

        t1, t2 = self.tasks
        unstarted = t1['status']
        yaml.load(t1.yaml)
        assert t1['status'] == unstarted, t1['status']
     

    def test_yaml_file(self):

        t1, t2 = self.tasks

        b = Bag()

        t1 = Task(b, title='Clean cat box dangit', creator='Matt',
            status=Status(b, title='unstarted'))

        print("t1['status'] is %s" % t1['status'])

        fp = t1.to_yaml_file('/tmp')

        print("status is %s" % t1['status'])

        new_t1 = Entity.from_yaml_file(fp, b)

        repr(t1)

        assert new_t1.uuid == t1.uuid

    def test_to_html(self):
        raise SkipTest


    def test_repr(self):
        
        t1, t2 = self.tasks

        print("t1 status is %(status)s" % t1)
        repr(t1)

