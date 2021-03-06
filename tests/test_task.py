# vim: set expandtab ts=4 sw=4 filetype=python:

import unittest

from pitz.entity import Estimate, Milestone, Person, Status, Tag
from pitz.entity.task import Task

class TestViews(unittest.TestCase):

    def setUp(self):

        self.t = Task(
            title='Bogus TestViews task',
            estimate=Estimate(title='really easy'),
            milestone=Milestone(title='9000'),
            owner=Person(title='Matt'),
            status=Status(title='unstarted'))


    def test_summarized_view(self):

        self.t.summarized_view

    def test_rst_interesting_attributes_view(self):

        self.t.rst_interesting_attributes_view

    def test_rst_tags_view(self):

        assert self.t.rst_tags_view == 'no tags', \
        self.t.rst_tags_view

class TestRstTagsView(unittest.TestCase):

    def setUp(self):

        self.t = Task(
            title='Bogus TestRstTagsView task',
            estimate=Estimate(title='really easy'),
            milestone=Milestone(title='9000'),
            owner=Person(title='Matt'),
            status=Status(title='unstarted'),

            tags=[
                Tag(title='time travel'),
                Tag(title='mind control')])

    def test_rst_tags_view(self):
        assert self.t.rst_tags_view
